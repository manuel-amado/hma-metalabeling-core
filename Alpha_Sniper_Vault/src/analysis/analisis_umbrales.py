# =============================================================================
# analisis_umbrales.py — HMA Meta-Labeling System
# Fase 3: Optimización Empírica del Umbral de Confianza (Threshold Tuning)
# Referencia teórica: López de Prado, AFML, Caps. 8 (F1-Score y Asimetría)
# =============================================================================
# FILOSOFÍA:
#   Cuando la Tasa Base (proporción real de TP) es muy baja (ej. 20-30%), 
#   pedirle al modelo que alcance una confianza de >0.60 puede ser irrealista, 
#   ya que las probabilidades calibradas tienden a oscilar alrededor de la 
#   tasa base. Este script escanea empíricamente cuál es el umbral matemático 
#   que maximiza nuestra Precision sin colapsar la cantidad de operaciones.
# =============================================================================

import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import TimeSeriesSplit, cross_val_predict
from sklearn.metrics import precision_recall_curve, precision_score, recall_score
from sklearn.base import clone

# Configuración visual
sns.set_theme(style="darkgrid", palette="viridis")

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
PROCESSED_PATH  = os.path.join(BASE_DIR, "output", "dataset_procesado.csv")
MODEL_PATH      = os.path.join(BASE_DIR, "output", "secondary_model_xgb.pkl")
PLOT_OUT_PATH   = os.path.join(BASE_DIR, "output", "precision_recall_curve.png")

FEATURE_COLS = [
    "Z_Score", "ATR_Norm", "RSI", "RSI_Extreme", "Bars_Since_Ext",
    "HMA_Slope_Pct", "HMA_Accel", "Trend_Align", "Dist_Macro_EMA",
    "Pullback_Dur", "Pullback_Depth_Pct", "Breakout_Force_ATR",
    "SL_Dist_ATR", "Spread_Pips", "Hour",
]
TARGET_COL = "Label_AI"


# =============================================================================
# 1. CARGA DE DATOS Y MODELO
# =============================================================================
def cargar_datos_y_modelo():
    if not os.path.exists(PROCESSED_PATH) or not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "[ERROR] Faltan archivos en output/. Asegúrate de ejecutar:\n"
            "1. pipeline_preprocesamiento.py\n2. entrenamiento_secondary_model.py"
        )

    print("[1/4] Cargando dataset y modelo...")
    df = pd.read_csv(PROCESSED_PATH, index_col="Time", parse_dates=True)
    df = df[df[TARGET_COL] != -1].copy()

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    artefactos = joblib.load(MODEL_PATH)
    modelo_base = artefactos["model"]

    # Como cross_val_predict hace el escalado interno si usáramos un pipeline,
    # pero aquí X_sc no tiene data leakage temporal si lo escalamos dinámicamente.
    # Crearemos un pipeline temporal.
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import RobustScaler
    
    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('xgb', clone(modelo_base)) # Clonamos para entrenarlo desde cero en la CV
    ])

    return X, y, pipeline


# =============================================================================
# 2. GENERACIÓN DE PROBABILIDADES OUT-OF-SAMPLE (TSS)
# =============================================================================
def generar_probabilidades_cv(X, y, pipeline):
    """
    Genera probabilidades predict_proba para todo el dataset, pero de forma 
    Out-Of-Sample, asegurando que cada predicción provenga de un modelo 
    entrenado ÚNICAMENTE con datos estrictamente anteriores.
    """
    print("[2/4] Generando probabilidades Out-Of-Sample (TimeSeriesSplit 5 folds)...")
    tss = TimeSeriesSplit(n_splits=5)
    
    # Pre-reservar un array con NaNs (los primeros datos de train puro quedarán como NaN)
    y_probs = np.full(len(X), np.nan)
    
    # Realizar CV manualmente para evitar el error de partición de cross_val_predict
    for train_idx, test_idx in tss.split(X):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test = X.iloc[test_idx]
        
        pipe_fold = clone(pipeline)
        pipe_fold.fit(X_train, y_train)
        
        # Extraer probabilidad de la Clase 1 y guardarla en sus índices
        y_probs[test_idx] = pipe_fold.predict_proba(X_test)[:, 1]

    return y_probs


# =============================================================================
# 3. CURVA PRECISION-RECALL
# =============================================================================
def graficar_pr_curve(y_real, y_probs):
    print("[3/4] Calculando y graficando Curva Precision-Recall...")
    
    precision, recall, thresholds = precision_recall_curve(y_real, y_probs)

    plt.figure(figsize=(10, 6))
    plt.plot(recall, precision, marker='.', label='XGBoost OOS (TSS)')
    
    # Linea base (Tasa Base de positivos)
    baseline = sum(y_real) / len(y_real)
    plt.axhline(y=baseline, color='r', linestyle='--', label=f'Tasa Base ({baseline:.2f})')
    
    plt.title('Curva Precision-Recall (Validación OOS Temporal)', fontsize=14)
    plt.xlabel('Recall (Tasa de Captura)', fontsize=12)
    plt.ylabel('Precision (Fiabilidad)', fontsize=12)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(PLOT_OUT_PATH, dpi=300)
    print(f"      -> Grafico guardado en: {PLOT_OUT_PATH}")


# =============================================================================
# 4. ESCANEO ITERATIVO DE UMBRALES
# =============================================================================
def escanear_umbrales(y_real, y_probs, umbral_min=0.30, umbral_max=0.60, step=0.01):
    print(f"[4/4] Escaneando umbrales de confianza desde {umbral_min:.2f} a {umbral_max:.2f}:\n")
    print("-" * 75)
    print(f"{'Umbral':^10} | {'Operaciones (Luz Verde)':^25} | {'Precision':^15} | {'Recall':^15}")
    print("-" * 75)

    resultados = []
    umbrales = np.arange(umbral_min, umbral_max + step, step)

    for umbral in umbrales:
        y_pred = (y_probs >= umbral).astype(int)
        
        n_operaciones = y_pred.sum()
        if n_operaciones == 0:
            prec = 0.0
            rec = 0.0
        else:
            prec = precision_score(y_real, y_pred, zero_division=0)
            rec = recall_score(y_real, y_pred, zero_division=0)
            
        resultados.append((umbral, n_operaciones, prec, rec))
        
        # Color verde si la Precision supera un 50%
        estado_prec = f"{prec:.2%}"
        if prec >= 0.50:
            estado_prec = f"⭐ {prec:.2%}"

        print(f"{umbral:^10.2f} | {n_operaciones:^25,} | {estado_prec:^15} | {rec:.2%}")

    print("-" * 75)
    print("\n[CONCLUSIÓN FINANCIERA]:")
    print("Busca el 'Umbral' donde la 'Precision' sea mayor al 50% (ideal >55%) ")
    print("y la cantidad de 'Operaciones' no sea tan baja que mate tu rentabilidad anual.")


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar_analisis():
    print("=" * 75)
    print("  HMA META-LABELING — OPTIMIZACIÓN DE UMBRAL DE CONFIANZA")
    print("=" * 75 + "\n")

    X, y, pipeline = cargar_datos_y_modelo()
    
    y_probs = generar_probabilidades_cv(X, y, pipeline)
    
    # cross_val_predict retorna NaNs para las filas usadas como entrenamiento
    # inicial del TimeSeriesSplit (el primer fold). Las removemos del análisis.
    indices_validos = ~np.isnan(y_probs)
    y_real_valid = y.iloc[indices_validos]
    y_probs_valid = y_probs[indices_validos]
    
    graficar_pr_curve(y_real_valid, y_probs_valid)
    escanear_umbrales(y_real_valid, y_probs_valid)

    print("\n[OK] Análisis completado exitosamente.\n")


if __name__ == "__main__":
    ejecutar_analisis()

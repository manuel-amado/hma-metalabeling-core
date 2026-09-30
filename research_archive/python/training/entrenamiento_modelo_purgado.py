# =============================================================================
# entrenamiento_modelo_purgado.py — HMA Meta-Labeling System
# Fase 3: Modelo Francotirador Purgado (6 Features de Alpha Puro)
# Referencia: SHAP audit -> Solo variables con Mean |SHAP| alto
# =============================================================================
# FILOSOFIA:
#   Despues del analisis SHAP, sabemos que 6 variables concentran el 80%
#   del poder predictivo real del modelo. Entrenar con las 15 features
#   originales introduce ruido estadistico que penaliza la Precision OOS.
#   Este script entrena exclusivamente con las 6 variables de Alpha puro.
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_score, recall_score
from sklearn.base import clone
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
OUT_DIR        = os.path.join(BASE_DIR, "output")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "Struct_Dataset_XAUUSD.csv")
MODEL_OUT_PATH = os.path.join(BASE_DIR, "output", "modelo_francotirador_purgado.pkl")
os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

# ── Features Activas (Top 6 SHAP — Alpha Puro) ───────────────────────────────
# Justificacion (SHAP audit):
#   1. SL_Dist_ATR (0.2456): La estructura del riesgo define el exito
#   2. Spread_Pips (0.2163): Microestructura: coste real de entrada
#   3. ATR_Norm    (0.1569): Regimen de volatilidad relativa
#   4. Dist_Macro_EMA (0.1539): Tension elastica vs EMA200
#   5. Breakout_Force_ATR (0.1154): Fisica del cruce
#   6. Pullback_Depth_Pct (0.0759): Profundidad de la correccion previa
FEATURES_ACTIVAS = [
    "SLDistATR",
    "Spread",
    "ATRNorm",
    "DistMacro",
    "BreakoutF",
    "PBDepth",
    "TrigCandleATR"
]
TARGET_COL = "Label"
N_SPLITS   = 5


# =============================================================================
# 1. CARGA Y PODA DEL DATASET
# =============================================================================
def cargar_y_podar(path: str = PROCESSED_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"[ERROR] No encontrado: {path}\n"
            "Ejecuta primero: python pipeline_preprocesamiento.py"
        )

    print("  Leyendo dataset purgado...")
    df = pd.read_csv(path)
    df = df[df[TARGET_COL] != -1].copy()

    missing = [c for c in FEATURES_ACTIVAS if c not in df.columns]
    if missing:
        raise ValueError(f"[ERROR] Features ausentes: {missing}")

    X = df[FEATURES_ACTIVAS]
    y = df[TARGET_COL]

    tasa_base = y.mean()
    print(f"  Dataset: {len(df):,} senales | Tasa Base: {tasa_base:.2%}")
    print(f"  Features activas ({len(FEATURES_ACTIVAS)}): {FEATURES_ACTIVAS}\n")
    return X, y


# =============================================================================
# 2. MODELO FRANCOTIRADOR CON CHALECO DE FUERZA MATEMATICO
# =============================================================================
def construir_modelo_purgado() -> XGBClassifier:
    """
    Regularizacion maxima: L1 + L2 con arboles superficiales.
    Sin scale_pos_weight: el desbalance es la realidad del mercado.
    """
    return XGBClassifier(
        max_depth=3,
        learning_rate=0.05,
        n_estimators=100,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=1.0,
        reg_lambda=2.0,
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )


# =============================================================================
# 3. GENERACION DE PROBABILIDADES OOS (MANUAL TSS)
# =============================================================================
def generar_probs_oos(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    tss = TimeSeriesSplit(n_splits=N_SPLITS)
    y_probs = np.full(len(X), np.nan)

    for fold_idx, (train_idx, val_idx) in enumerate(tss.split(X), start=1):
        X_train_raw, X_val_raw = X.iloc[train_idx], X.iloc[val_idx]
        y_train = y.iloc[train_idx]

        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc   = scaler.transform(X_val_raw)

        modelo = construir_modelo_purgado()
        modelo.fit(X_train_sc, y_train)

        y_probs[val_idx] = modelo.predict_proba(X_val_sc)[:, 1]
        print(f"  [Fold {fold_idx}/{N_SPLITS}] Train: {len(train_idx):,} | Val: {len(val_idx):,} OK")

    return y_probs


# =============================================================================
# 4. ESCANEO DE UMBRALES
# =============================================================================
def escanear_umbrales(y_real: pd.Series, y_probs: np.ndarray):
    print("\n" + "=" * 60)
    print("  ESCANEO DE UMBRALES (Features Purgadas)")
    print("=" * 60)
    print(f"  {'Umbral':^8} | {'Luz Verde':^15} | {'Precision':^12} | {'Recall':^10}")
    print("-" * 60)

    umbrales = np.arange(0.40, 0.61, 0.02)
    for umbral in umbrales:
        y_pred = (y_probs >= umbral).astype(int)
        n_ops  = y_pred.sum()
        prec   = precision_score(y_real, y_pred, zero_division=0) if n_ops > 0 else 0.0
        rec    = recall_score(y_real, y_pred, zero_division=0)    if n_ops > 0 else 0.0
        marca  = " (*)" if prec >= 0.50 else ""
        print(f"  {umbral:^8.2f} | {n_ops:^15,} | {prec:^11.2%}{marca} | {rec:^10.2%}")

    print("-" * 60)
    print("  (*) Umbral con Precision >= 50%\n")


# =============================================================================
# 5. ENTRENAMIENTO FINAL Y GUARDADO
# =============================================================================
def entrenar_y_guardar(X: pd.DataFrame, y: pd.Series):
    print("[MODELO FINAL] Entrenando sobre todo el historial...")
    scaler_final = RobustScaler()
    X_sc = scaler_final.fit_transform(X)

    modelo_final = construir_modelo_purgado()
    modelo_final.fit(X_sc, y)

    artefacto = {
        "model":           modelo_final,
        "scaler":          scaler_final,
        "features_activas": FEATURES_ACTIVAS,
        "threshold":       0.50,  # Ajustar con el resultado del escaneo
    }
    joblib.dump(artefacto, MODEL_OUT_PATH)
    print(f"[MODELO FINAL] Guardado en: {MODEL_OUT_PATH}\n")
    return modelo_final


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar():
    print("=" * 60)
    print("  HMA META-LABELING — MODELO FRANCOTIRADOR PURGADO")
    print("  Features SHAP-Auditadas: 6 Variables de Alpha Puro")
    print("=" * 60 + "\n")

    print("[1/4] Cargando y podando dataset...")
    X, y = cargar_y_podar()

    print("[2/4] Generando probabilidades OOS (TimeSeriesSplit 5 folds)...")
    y_probs = generar_probs_oos(X, y)

    # Filtrar filas sin probabilidad OOS (primer bloque de train puro)
    indices_validos  = ~np.isnan(y_probs)
    y_real_valid     = y[indices_validos]
    y_probs_valid    = y_probs[indices_validos]
    print(f"  Total muestras OOS evaluadas: {len(y_real_valid):,}\n")

    print("[3/4] Escaneando umbrales de confianza...")
    escanear_umbrales(y_real_valid, y_probs_valid)

    print("[4/4] Entrenando y guardando modelo final...")
    entrenar_y_guardar(X, y)

    print("[OK] Entrenamiento del modelo purgado completado.\n")


if __name__ == "__main__":
    ejecutar()

# =============================================================================
# analisis_shap_features.py — HMA Meta-Labeling System
# Fase 2: Reduccion de Dimensionalidad via Teoria de Juegos (SHAP)
# Referencia teorica: Lundberg & Lee (2017) + AFML Cap. 8 (Feature Importance)
# =============================================================================
# FILOSOFIA:
#   Las Feature Importances clasicas de XGBoost (gain/frequency) son
#   estadisticamente inestables y estan sesgadas hacia variables con muchos
#   valores unicos. Los Valores SHAP (SHapley Additive exPlanations) asignan
#   a cada variable su contribucion marginal real a cada prediccion individual,
#   promediando sobre todas las posibles combinaciones. Es la unica metrica
#   de importancia con fundamentacion en Teoria de Juegos (Shapley, 1953).
#   Resultado: sabemos EXACTAMENTE que variables aportan Alpha real y cuales
#   son ruido estadistico que hay que extirpar del sistema MQL5.
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")  # Backend sin entorno visual (compatible con Windows headless)
import matplotlib.pyplot as plt

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
PROCESSED_PATH = os.path.join(BASE_DIR, "output", "dataset_procesado.csv")
PLOT_BAR_PATH  = os.path.join(BASE_DIR, "output", "shap_summary_bar.png")

# ── Columnas canonicas ────────────────────────────────────────────────────────
FEATURE_COLS = [
    "Z_Score",           # Posicion estadistica del precio vs SMA20 (en sigma)
    "ATR_Norm",          # Volatilidad relativa: ATR_actual / ATR_medio_10p
    "RSI",               # Momentum en la barra del cruce (Wilder 14p)
    "RSI_Extreme",       # RSI minimo/maximo en la ventana de lookback
    "Bars_Since_Ext",    # Latencia entre el extremo RSI y el cruce (velas)
    "HMA_Slope_Pct",     # 1a derivada de HMA: inercia direccional
    "HMA_Accel",         # 2a derivada de HMA: aceleracion o agotamiento
    "Trend_Align",       # Contexto macro: +1=a favor, -1=contra-tendencia
    "Dist_Macro_EMA",    # (Close - EMA200_H4) / ATR: tension elastica macro
    "Pullback_Dur",      # Velas que el precio paso al otro lado de la HMA
    "Pullback_Depth_Pct",# Profundidad maxima del pullback en multiples de ATR
    "Breakout_Force_ATR",# |Close - HMA| / ATR: fuerza de ruptura normalizada
    "SL_Dist_ATR",       # Distancia al Stop Loss en multiples de ATR
    "Spread_Pips",       # Spread en pips (microestructura de liquidez)
    "Hour",              # Hora del servidor 0-23 (estacionalidad intradia)
]
TARGET_COL = "Label_AI"
N_SPLITS   = 3   # 3 folds: mas datos por fold para el SHAP en datasets medianos


# =============================================================================
# 1. CARGA DEL DATASET PROCESADO
# =============================================================================
def cargar_datos(path: str = PROCESSED_PATH) -> tuple:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"[ERROR] No se encontro: {path}\n"
            "Ejecuta primero: python pipeline_preprocesamiento.py"
        )

    df = pd.read_csv(path, index_col="Time", parse_dates=True)

    # Filtrar cierres por tiempo (Label_AI == -1)
    df = df[df[TARGET_COL] != -1].copy()

    # Validar que las features existen en el dataset procesado
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"[ERROR] Features ausentes en el dataset: {missing}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    tasa_base = y.mean()
    print(f"  Dataset: {len(df):,} senales | Tasa Base (% TPs): {tasa_base:.2%}")
    print(f"  Rango temporal: {df.index.min()} -> {df.index.max()}\n")
    return X, y


# =============================================================================
# 2. MODELO XGBoost EXTREMADAMENTE REGULARIZADO
# =============================================================================
def construir_modelo_regularizado() -> XGBClassifier:
    """
    Hiperparametros diseñados para evitar la memorizacion de ruido:
      max_depth=3:       Arboles muy superficiales. Solo captura relaciones
                         de orden 1-2 entre features. Fuerza al modelo a usar
                         solo las variables MAS relevantes.
      n_estimators=100:  Pocos arboles. Suficiente para el analisis SHAP
                         sin overfitting en el set de validacion.
      learning_rate=0.05: Shrinkage conservador.
      reg_alpha=1.5:     Regularizacion L1 (Lasso): empuja los pesos de
                         features irrelevantes exactamente a 0.
      reg_lambda=1.5:    Regularizacion L2 (Ridge): penaliza pesos grandes,
                         dispersando la importancia uniformemente.
    La combinacion de L1+L2 con arboles superficiales garantiza que solo
    las features con verdadero poder predictivo OOS sobrevivan.
    """
    return XGBClassifier(
        max_depth=3,
        learning_rate=0.05,
        n_estimators=100,
        reg_alpha=1.5,
        reg_lambda=1.5,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )


# =============================================================================
# 3. LOOP DE VALIDACION TEMPORAL + ACUMULACION DE SHAP
# =============================================================================
def calcular_shap_oos(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    """
    Calcula Valores SHAP Out-Of-Sample para todo el dataset usando TSS.

    Por que OOS y no In-Sample:
      Los valores SHAP calculados en datos de entrenamiento estan inflados:
      el modelo "conoce" esos ejemplos y les asigna importancias engañosas.
      Al calcular SHAP solo en el set de VALIDACION de cada fold, obtenemos
      una medida honesta de que variables son utiles para predecir datos
      que el modelo nunca ha visto. Esto es el Alpha real.

    Returns:
        shap_values_oos: Array (n_muestras, n_features) con valores SHAP
                         acumulados de todos los folds de validacion.
    """
    tss = TimeSeriesSplit(n_splits=N_SPLITS)

    # Pre-reservar con NaN: las filas del primer bloque de entrenamiento puro
    # no tendran SHAP values calculados.
    shap_acumulados = np.full((len(X), len(FEATURE_COLS)), np.nan)

    print(f"  Ejecutando {N_SPLITS} folds de validacion temporal...\n")

    for fold_idx, (train_idx, val_idx) in enumerate(tss.split(X), start=1):
        X_train_raw = X.iloc[train_idx]
        X_val_raw   = X.iloc[val_idx]
        y_train     = y.iloc[train_idx]

        # Escalado interno por fold (anti-leakage estricto)
        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc   = scaler.transform(X_val_raw)

        # Convertir a DataFrame para que SHAP pueda leer los nombres de columna
        X_train_df = pd.DataFrame(X_train_sc, columns=FEATURE_COLS)
        X_val_df   = pd.DataFrame(X_val_sc,   columns=FEATURE_COLS)

        # Entrenar modelo regularizado
        modelo = construir_modelo_regularizado()
        modelo.fit(X_train_df, y_train)

        # Calcular SHAP con TreeExplainer (exacto y eficiente para XGBoost)
        explainer   = shap.TreeExplainer(modelo)
        shap_vals   = explainer.shap_values(X_val_df)

        # Guardar en las posiciones correctas del array global
        shap_acumulados[val_idx] = shap_vals

        print(f"  [Fold {fold_idx}/{N_SPLITS}] Train: {len(train_idx):,} | "
              f"Val: {len(val_idx):,} -> SHAP calculados OK")

    # Filtrar las filas donde no hay SHAP (primer bloque de entrenamiento puro)
    indices_validos  = ~np.isnan(shap_acumulados[:, 0])
    shap_validos     = shap_acumulados[indices_validos]

    print(f"\n  Total muestras con SHAP OOS: {len(shap_validos):,}\n")
    return shap_validos


# =============================================================================
# 4. TABLA RANKING DE ALPHA
# =============================================================================
def imprimir_ranking_alpha(shap_values: np.ndarray):
    """
    Imprime una tabla clasificada con el Mean |SHAP Value| de cada feature.

    Por que |SHAP| y no SHAP directo:
      Los valores SHAP pueden ser positivos (contribuyen a predecir TP=1)
      o negativos (contribuyen a predecir fracaso=0). Para medir la
      MAGNITUD del impacto total de una variable independientemente de
      su direccion, usamos el valor absoluto medio. Una variable con
      Mean |SHAP| alto es influyente (para bien o para mal).
      Una variable con Mean |SHAP| ~ 0 es ruido estadistico puro.
    """
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    ranking = pd.Series(mean_abs_shap, index=FEATURE_COLS).sort_values(ascending=False)

    print("=" * 65)
    print("  RANKING DE ALPHA — MEAN |SHAP VALUE| (OOS TEMPORAL)")
    print("=" * 65)
    print(f"  {'Pos':>4} | {'Feature':<22} | {'Mean |SHAP|':>14} | Estado")
    print("-" * 65)

    for pos, (feat, val) in enumerate(ranking.items(), start=1):
        # Clasificar la señal de Alpha de cada variable
        if val >= 0.010:
            estado = "[ALPHA FUERTE]"
        elif val >= 0.005:
            estado = "[ALPHA MARGINAL]"
        else:
            estado = "[RUIDO - EXTIRPAR]"

        print(f"  {pos:>4} | {feat:<22} | {val:>14.6f} | {estado}")

    print("-" * 65)
    print("\n  CANDIDATAS A ELIMINAR (Mean |SHAP| < 0.005):")
    ruido = ranking[ranking < 0.005]
    if ruido.empty:
        print("  Ninguna. Todas las features aportan señal estadistica.")
    else:
        for feat, val in ruido.items():
            print(f"    - {feat} ({val:.6f})")
    print()

    return ranking


# =============================================================================
# 5. GRAFICO SHAP SUMMARY BAR
# =============================================================================
def guardar_shap_bar(shap_values: np.ndarray, X_sample: pd.DataFrame):
    """
    Genera y guarda el grafico de barras SHAP.
    Muestra el Mean |SHAP Value| global por feature, ordenado de mayor a menor.
    """
    plt.figure()
    shap.summary_plot(
        shap_values,
        features=X_sample,
        feature_names=FEATURE_COLS,
        plot_type="bar",
        show=False,
        max_display=15,
    )
    plt.tight_layout()
    plt.savefig(PLOT_BAR_PATH, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafico SHAP guardado en: {PLOT_BAR_PATH}\n")


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar_analisis_shap():
    print("=" * 65)
    print("  HMA META-LABELING — ANALISIS SHAP (TEORIA DE JUEGOS)")
    print("=" * 65 + "\n")

    print("[1/4] Cargando dataset procesado...")
    X, y = cargar_datos()

    print("[2/4] Calculando SHAP Out-Of-Sample (TimeSeriesSplit 3 folds)...")
    shap_oos = calcular_shap_oos(X, y)

    print("[3/4] Generando ranking de Alpha y grafico SHAP...")
    ranking = imprimir_ranking_alpha(shap_oos)

    # Para el grafico usamos una muestra del dataset alineada con los SHAP OOS
    # Los primeros N indices no tienen SHAP (eran pure-train del fold 1)
    n_sin_shap = len(X) - len(shap_oos)
    X_valida   = X.iloc[n_sin_shap:].copy()

    # Escalar para que los nombres de columna sean correctos en el grafico
    X_valida_sc = pd.DataFrame(
        RobustScaler().fit_transform(X_valida),
        columns=FEATURE_COLS
    )

    guardar_shap_bar(shap_oos, X_valida_sc)

    print("[4/4] Analisis completado.")
    print("=" * 65)
    print("  INTERPRETACION FINANCIERA:")
    print("  Las variables [RUIDO] pueden eliminarse del MQL5_Engine")
    print("  para reducir el overfitting y aumentar la robustez Cross-Asset.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    ejecutar_analisis_shap()

# =============================================================================
# optimizar_salidas_mfe.py — HMA Meta-Labeling System
# Fase 4: Optimizacion de Salidas Sinteticas via MFE (Max Favorable Excursion)
# =============================================================================
# FILOSOFIA (Lopez de Prado, AFML Cap. 3 — "The Three Barriers"):
#   El Take Profit del bot MQL5 es un parametro arbitrario. La columna
#   'Max_RR_Achieved' nos dice HASTA DONDE LLEGO el precio realmente
#   (en terminos de R:R) antes de volver o tocar el SL.
#   Esto nos permite SIMULAR cualquier nivel de TP sinteticamente:
#     "Si hubiera cerrado en TP=1.5R, cuantas de estas operaciones
#      habrían llegado ahi antes del SL?"
#   El objetivo es encontrar el TP que maximiza la Tasa Base (% victorias)
#   sin destruir la cantidad de senales aprovechables.
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_score, recall_score
from sklearn.base import clone
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
PROCESSED_PATH = os.path.join(BASE_DIR, "output", "dataset_procesado.csv")

# ── Configuracion del Experimento ─────────────────────────────────────────────
TARGETS_RR = [1.2, 1.5, 2.0]   # Tres escenarios de TP a simular

# ── Features SHAP-Auditadas (6 variables de Alpha puro) ──────────────────────
FEATURES_ACTIVAS = [
    "SL_Dist_ATR",
    "Spread_Pips",
    "ATR_Norm",
    "Dist_Macro_EMA",
    "Breakout_Force_ATR",
    "Pullback_Depth_Pct",
]
N_SPLITS = 5


# =============================================================================
# 1. CARGA DEL DATASET
# =============================================================================
def cargar_dataset(path: str = PROCESSED_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"[ERROR] No encontrado: {path}\n"
            "Ejecuta primero: python pipeline_preprocesamiento.py"
        )

    df = pd.read_csv(path, index_col="Time", parse_dates=True)

    if "Max_RR_Achieved" not in df.columns:
        raise KeyError(
            "[ERROR] Columna 'Max_RR_Achieved' ausente en el dataset.\n"
            "Requiere el nuevo EA v2.1 con ML_Logger actualizado y un nuevo backtest."
        )

    missing = [c for c in FEATURES_ACTIVAS if c not in df.columns]
    if missing:
        raise ValueError(f"[ERROR] Features ausentes: {missing}")

    print(f"  Senales disponibles: {len(df):,}")
    print(f"  Rango: {df.index.min()} -> {df.index.max()}\n")
    return df


# =============================================================================
# 2. RE-LABELING DINAMICO POR MFE
# =============================================================================
def relabel_por_mfe(df: pd.DataFrame, target_rr: float) -> pd.Series:
    """
    Genera una nueva variable objetivo 'y' sintetica para un TP dado.

    LOGICA FINANCIERA:
      Si Max_RR_Achieved >= target_rr, el precio llego a ese nivel de TP
      antes de que se cerrara la operacion. Por tanto, si hubieramos puesto
      el TP en ese nivel, la operacion habria sido ganadora (Label=1).
      De lo contrario, habria tocado el SL antes (Label=0).

      Esta simulacion es OPTIMISTA (sin slippage de ejecucion del TP),
      pero valida como experimento de rango aceptable.
    """
    y_sintetico = (df["Max_RR_Achieved"] >= target_rr).astype(int)
    tasa_base   = y_sintetico.mean()
    n_ganadoras = y_sintetico.sum()
    print(f"  Re-labeling @ TP={target_rr}R: "
          f"{n_ganadoras:,} ganadoras / {len(y_sintetico):,} total "
          f"(Tasa Base = {tasa_base:.2%})")
    return y_sintetico


# =============================================================================
# 3. MODELO XGBoost ULTRA-REGULARIZADO
# =============================================================================
def construir_modelo() -> XGBClassifier:
    """
    Mismo chaleco de fuerza matematico que entrenamiento_modelo_purgado.py.
    Sin scale_pos_weight: dejamos que el desbalance natural dicte el umbral.
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
# 4. GENERACION PROBABILIDADES OOS (TSS manual)
# =============================================================================
def generar_probs_oos(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    tss    = TimeSeriesSplit(n_splits=N_SPLITS)
    probs  = np.full(len(X), np.nan)

    for fold_idx, (train_idx, val_idx) in enumerate(tss.split(X), start=1):
        X_train_raw = X.iloc[train_idx]
        X_val_raw   = X.iloc[val_idx]
        y_train     = y.iloc[train_idx]

        # Escalado anti-leakage: ajustado solo con train del fold
        scaler     = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc   = scaler.transform(X_val_raw)

        modelo = construir_modelo()
        modelo.fit(X_train_sc, y_train)
        probs[val_idx] = modelo.predict_proba(X_val_sc)[:, 1]

    return probs


# =============================================================================
# 5. ESCANEO DE UMBRALES Y TABLA DE SALIDA
# =============================================================================
def escanear_e_imprimir(y_real: pd.Series, y_probs: np.ndarray, target_rr: float):
    """
    Imprime la tabla de umbrales 0.44 -> 0.58 para el escenario dado.
    """
    print(f"\n{'='*58}")
    print(f"  SIMULACION TARGET R:R = {target_rr}")
    print(f"{'='*58}")
    print(f"  {'Umbral':^8} | {'Luz Verde':^16} | {'Precision':^14}")
    print(f"  {'-'*8}-+-{'-'*16}-+-{'-'*14}")

    umbrales = np.arange(0.44, 0.59, 0.02)
    mejor_prec = 0.0
    mejor_umbral = None

    for umbral in umbrales:
        y_pred = (y_probs >= umbral).astype(int)
        n_ops  = y_pred.sum()
        prec   = precision_score(y_real, y_pred, zero_division=0) if n_ops > 0 else 0.0
        marca  = " (*)" if prec >= 0.50 else "     "

        print(f"  {umbral:^8.2f} | {n_ops:^16,} | {prec:^10.2%}{marca}")

        if prec > mejor_prec:
            mejor_prec    = prec
            mejor_umbral  = umbral

    print(f"  {'='*58}")
    if mejor_umbral is not None:
        print(f"  Mejor resultado: Umbral={mejor_umbral:.2f} -> Precision={mejor_prec:.2%}")
    print()


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar():
    print("=" * 58)
    print("  HMA META-LABELING — OPTIMIZACION DE SALIDAS MFE")
    print("  Simulacion de 3 niveles de Take Profit Sintetico")
    print("=" * 58 + "\n")

    print("[1/3] Cargando dataset procesado...")
    df = cargar_dataset()
    X  = df[FEATURES_ACTIVAS]

    # Iterar sobre cada escenario de TP
    for target_rr in TARGETS_RR:
        print(f"[2/3] Re-labeling sintetico para TP = {target_rr}R...")
        y = relabel_por_mfe(df, target_rr)

        print(f"[3/3] Entrenamiento OOS (TSS {N_SPLITS} folds)...")
        y_probs = generar_probs_oos(X, y)

        # Filtrar indices sin probabilidad OOS (bloque de train puro del fold 1)
        validos      = ~np.isnan(y_probs)
        y_valid      = y[validos]
        y_probs_valid = y_probs[validos]

        escanear_e_imprimir(y_valid, y_probs_valid, target_rr)

    print("[OK] Analisis de optimizacion de salidas completado.\n")
    print("INTERPRETACION:")
    print("  Busca el escenario TP donde la Tasa Base sea mas alta")
    print("  Y donde algun umbral supere el 50% de Precision (*).")
    print("  Ese TP es el nivel optimo para el EA en produccion.\n")


if __name__ == "__main__":
    ejecutar()

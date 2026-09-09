# =============================================================================
# entrenamiento_secondary_model.py — HMA Meta-Labeling System
# Fase 2: Entrenamiento del Modelo Secundario (FRANCOTIRADOR - ALTA PRECISIÓN)
# Referencia teórica: López de Prado, AFML, Caps. 7-8
# =============================================================================
# FILOSOFÍA:
#   El Modelo Secundario actúa como un filtro de precisión sobre el Modelo
#   Primario (bot MQL5 de alto recall). Su objetivo no es maximizar Accuracy
#   ni Recall, sino maximizar Precision en la Clase 1: cuando diga "opera",
#   que tenga razón casi siempre. Un falso positivo del Modelo Secundario es
#   una pérdida real de capital en producción.
#
#   Enfoque Francotirador:
#   1. Sin balanceo artificial de clases (el desbalance es la realidad).
#   2. Umbral de confianza estricto (prob > 0.60).
#   3. Validación Temporal estricta (TimeSeriesSplit).
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    f1_score,
    precision_score,
)
from xgboost import XGBClassifier

# Silenciar warnings no críticos de XGBoost durante CV
warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
PROCESSED_PATH  = os.path.join(BASE_DIR, "output", "dataset_procesado.csv")
SCALER_PATH     = os.path.join(BASE_DIR, "output", "robust_scaler.pkl")
MODEL_OUT_PATH  = os.path.join(BASE_DIR, "output", "secondary_model_xgb.pkl")
os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

# ── Configuración Francotirador ───────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.60  # Umbral estricto para predecir 1
N_SPLITS = 5                 # Número de ventanas temporales encadenadas

# ── Columnas (deben coincidir exactamente con pipeline_preprocesamiento.py) ───
FEATURE_COLS = [
    "Z_Score", "ATR_Norm", "RSI", "RSI_Extreme", "Bars_Since_Ext",
    "HMA_Slope_Pct", "HMA_Accel", "Trend_Align", "Dist_Macro_EMA",
    "Pullback_Dur", "Pullback_Depth_Pct", "Breakout_Force_ATR",
    "SL_Dist_ATR", "Spread_Pips", "Hour",
]
TARGET_COL = "Label_AI"


# =============================================================================
# 1. CARGA DEL DATASET PROCESADO
# =============================================================================
def cargar_datos_procesados(path: str = PROCESSED_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"[ERROR] Dataset procesado no encontrado en: {path}\n"
            "Ejecuta primero: python pipeline_preprocesamiento.py"
        )

    df = pd.read_csv(path, index_col="Time", parse_dates=True)

    if TARGET_COL not in df.columns:
        raise KeyError(
            f"[ERROR] La columna objetivo '{TARGET_COL}' no está en el dataset.\n"
            "Verifica que pipeline_preprocesamiento.py se ejecutó correctamente."
        )

    # Filtrar señales sin resolución (Label_AI == -1: cierre por tiempo).
    n_total = len(df)
    df = df[df[TARGET_COL] != -1].copy()
    n_tiempo = n_total - len(df)
    print(f"[CARGA] Dataset: {len(df):,} señales binarias "
          f"({n_tiempo:,} cierres por tiempo excluidos)")
    print(f"  → Distribución Label_AI:\n{df[TARGET_COL].value_counts()}\n")
    return df


# =============================================================================
# 2. CONSTRUCCIÓN DEL MODELO XGBoost (Alta Precisión)
# =============================================================================
def construir_modelo() -> XGBClassifier:
    """
    Configura XGBClassifier con hiperparámetros orientados a la Precisión.
    Cero balanceo artificial: scale_pos_weight se deja en 1 (default) para
    no inflar artificialmente las probabilidades de la clase minoritaria.
    """
    return XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )


# =============================================================================
# 3. VALIDACIÓN CRUZADA TEMPORAL (TimeSeriesSplit)
# =============================================================================
def validar_con_tss(X: pd.DataFrame, y: pd.Series, n_splits: int = N_SPLITS):
    """
    Ejecuta validación cruzada con ventanas temporales encadenadas y extrae
    métricas basadas en el Custom Confidence Threshold. También acumula las
    Feature Importances para auditoría de Alpha.
    """
    from sklearn.preprocessing import RobustScaler as RS

    tss = TimeSeriesSplit(n_splits=n_splits)
    metrics_por_fold = []
    fold_importances = []
    modelos = []

    print("=" * 65)
    print(f"  VALIDACIÓN CRUZADA TEMPORAL — {n_splits} Folds")
    print(f"  Umbral de Probabilidad Dinámico: >= {CONFIDENCE_THRESHOLD}")
    print("=" * 65)

    for fold_idx, (train_idx, test_idx) in enumerate(tss.split(X), start=1):
        X_train_raw = X.iloc[train_idx]
        X_test_raw  = X.iloc[test_idx]
        y_train     = y.iloc[train_idx]
        y_test      = y.iloc[test_idx]

        # ── Escalado interno por fold (anti-leakage) ─────────────────────────
        scaler_fold = RS()
        X_train_sc  = scaler_fold.fit_transform(X_train_raw)
        X_test_sc   = scaler_fold.transform(X_test_raw)

        # ── Entrenar ──────────────────────────────────────────────────────────
        modelo = construir_modelo()
        modelo.fit(X_train_sc, y_train)
        modelos.append(modelo)

        # Acumular Feature Importances
        fold_importances.append(modelo.feature_importances_)

        # ── Predecir con Umbral Estricto ──────────────────────────────────────
        y_probs = modelo.predict_proba(X_test_sc)[:, 1]
        y_pred  = (y_probs >= CONFIDENCE_THRESHOLD).astype(int)

        prec  = precision_score(y_test, y_pred, zero_division=0)
        f1    = f1_score(y_test, y_pred, zero_division=0)
        cm    = confusion_matrix(y_test, y_pred, labels=[0, 1])

        n_tp_pred = (y_pred == 1).sum()

        metrics_por_fold.append({
            "fold":      fold_idx,
            "precision": prec,
            "f1":        f1,
            "n_test":    len(y_test),
            "n_pred_1":  n_tp_pred,
            "cm":        cm,
        })

        print(f"\n── Fold {fold_idx}/{n_splits} "
              f"[Train: {len(y_train):,} | Test: {len(y_test):,}] ──")
        print(f"  Señales que superan umbral ({CONFIDENCE_THRESHOLD}): {n_tp_pred:,}")
        print(f"  Precision Clase 1:  {prec:.4f}")
        print(f"  Matriz de Confusión:\n"
              f"            Pred 0   Pred 1\n"
              f"  Real 0  [{cm[0,0]:>6}] [{cm[0,1]:>6}]\n"
              f"  Real 1  [{cm[1,0]:>6}] [{cm[1,1]:>6}]")
        print(f"\n  Reporte de Clasificación:\n"
              f"{classification_report(y_test, y_pred, target_names=['Fracaso(0)','TP(1)'], zero_division=0)}")

    return metrics_por_fold, fold_importances, modelos


# =============================================================================
# 4. REPORTE AGREGADO Y FEATURE IMPORTANCES
# =============================================================================
def imprimir_resumen_y_alpha(metrics_por_fold: list, fold_importances: list):
    """
    Imprime resumen estadístico de la CV y el top de Feature Importances
    promediado sobre todos los folds.
    """
    precisiones = [m["precision"] for m in metrics_por_fold]
    f1s         = [m["f1"]        for m in metrics_por_fold]
    n_preds     = [m["n_pred_1"]  for m in metrics_por_fold]

    print("\n" + "=" * 65)
    print("  RESUMEN AGREGADO — SISTEMA FRANCOTIRADOR")
    print("=" * 65)
    print(f"  Media Precision: {np.mean(precisiones):.4f} ± {np.std(precisiones):.4f}")
    print(f"  Media F1-Score:  {np.mean(f1s):.4f} ± {np.std(f1s):.4f}")
    print(f"  Promedio de disparos por fold: {np.mean(n_preds):.1f}")

    # Diagnóstico estricto
    media_prec = np.mean(precisiones)
    if media_prec >= 0.65:
        estado = "✅ INSTITUCIONAL — Alta precisión. Sistema listo para operar."
    elif media_prec >= 0.55:
        estado = "⚠️  ACEPTABLE — Rentabilidad marginal. Revisa features para subir Precision."
    else:
        estado = "❌ INSUFICIENTE — Alto ruido. Cuidado en producción."

    print(f"\n  Diagnóstico: {estado}\n")

    # Auditoría de Alpha (Feature Importances)
    print("-" * 65)
    print("  AUDITORÍA DE ALPHA: TOP 10 FEATURE IMPORTANCES (Promedio CV)")
    print("-" * 65)
    
    avg_importances = np.mean(fold_importances, axis=0)
    fi_series = pd.Series(avg_importances, index=FEATURE_COLS).sort_values(ascending=False)
    
    for i, (feat, imp) in enumerate(fi_series.head(10).items(), 1):
        print(f"  {i:>2}. {feat:<20} : {imp:.4f}")
    print("-" * 65 + "\n")


# =============================================================================
# 5. ENTRENAMIENTO FINAL (modelo sobre todo el dataset)
# =============================================================================
def entrenar_modelo_final(X: pd.DataFrame, y: pd.Series) -> XGBClassifier:
    """
    Entrena el modelo de producción final sin leakage ni balanceo.
    Se utilizará en inferencia aplicando predict_proba() >= CONFIDENCE_THRESHOLD.
    """
    from sklearn.preprocessing import RobustScaler as RS

    print("[MODELO FINAL] Entrenando modelo de producción sobre todo el historial...")
    scaler_final = RS()
    X_sc = scaler_final.fit_transform(X)

    modelo_final = construir_modelo()
    modelo_final.fit(X_sc, y)

    joblib.dump({"model": modelo_final, "scaler": scaler_final, "threshold": CONFIDENCE_THRESHOLD}, MODEL_OUT_PATH)
    print(f"[MODELO FINAL] Guardado en: {MODEL_OUT_PATH}")
    return modelo_final


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar_entrenamiento():
    print("=" * 65)
    print("  HMA META-LABELING — ENTRENAMIENTO MODELO SECUNDARIO")
    print("=" * 65 + "\n")

    # 1. Cargar datos procesados
    df = cargar_datos_procesados()
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # 2. Validación cruzada temporal (Francotirador)
    metrics, fold_importances, _ = validar_con_tss(X, y, n_splits=N_SPLITS)

    # 3. Resumen agregado y auditoría de variables
    imprimir_resumen_y_alpha(metrics, fold_importances)

    # 4. Entrenar y guardar modelo final
    # Guardamos el modelo siempre para propósitos de análisis/testing local,
    # el trader decide si ponerlo en producción o no basándose en el Diagnóstico.
    entrenar_modelo_final(X, y)

    print("\n[OK] Entrenamiento completado.\n")


if __name__ == "__main__":
    ejecutar_entrenamiento()

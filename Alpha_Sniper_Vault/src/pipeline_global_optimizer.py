# =============================================================================
# pipeline_global_optimizer.py -- HMA Meta-Labeling System
# Autor: Manuel
# Fase 7: Dual-Inference Crossover & Hyperspace Optimization
#
# USO (desde cualquier directorio):
#   cd C:\Users\Manuel\Desktop\HMA_MetaLabeling\Python_ML
#   .venv\Scripts\python.exe pipeline_global_optimizer.py
#
# FILOSOFIA:
#   Entradas y salidas son un ecosistema acoplado. Este script:
#   1. Entrena el Modelo de Entradas (Entry Model) sobre Struct_Dataset_*.csv
#   2. Entrena el Modelo de Salidas  (Exit Model)  sobre HMA_Exit_Dataset_*.csv
#   3. Realiza un backtest vectorizado 2D:
#        Eje X -- Entry_Threshold (prob entrada   : 0.40 -> 0.75)
#        Eje Y -- Exit_Threshold  (prob exit model : 0.40 -> 0.80)
#   4. Evalua cada combo con el Alpha Score institucional:
#        Alpha = (Sharpe * Annual_R) / (MaxDD_Pct + 0.1)
#   5. Reporta los 3 perfiles ganadores (A=Agresivo, B=Balanceado, C=Conservador)
#      y serializa los modelos + umbrales para produccion MQL5.
#
# ZERO DATA LEAKAGE:
#   - LEAKAGE_COLS nunca llegan a los modelos
#   - El Exit Model solo usa informacion disponible en el momento del amago
#   - El merge se hace DESPUES del entrenamiento individual de cada modelo
# =============================================================================

# Forzar UTF-8 en stdout/stderr ANTES de cualquier otro import.
# Elimina la necesidad de PYTHONUTF8=1 como variable de entorno externa.
import os
import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import warnings
import itertools
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import TimeSeriesSplit
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import QuantileTransformer

warnings.filterwarnings("ignore", category=UserWarning)

# =============================================================================
# ── CONFIGURACIÓN GLOBAL ─────────────────────────────────────────────────────
# =============================================================================

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUT_DIR  = os.path.join(BASE_DIR, "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Variables globales de archivo eliminadas para habilitar bucle multi-activo

# ── Columnas de fuga de datos — NUNCA entran en los modelos ──────────────────
LEAKAGE_COLS = [
    "Realized_RR",     # Resultado final del trade — futuro puro
    "MAE_Pct",         # Calculado post-cierre
    "MFE_Pct",         # Calculado post-cierre
    "Return_Pct",      # Derivado del cierre
    "Bars_In_Trade",   # Conocido solo al cerrar
    "Label",           # El target mismo
    # Metadatos no predictivos
    "Ticket", "Time", "Signal",
    # En exit dataset: el resultado también es futuro
    "Missed_Profit_R",
]

# ── Features del Modelo de Entradas ──────────────────────────────────────────
ENTRY_FEATURES = [
    "Z_Score", "ATR_Norm", "Cross_Vol_Regime", "Fract_Diff_Return",
    "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", 
    "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour",
    "Session_Time", "H4_Trend_Align",
    "ATR_Ratio_High", "Energy_Accumulation",
    "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep",
    "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR", "Is_Asian_Sweep",
    "Spread_Expansion_Ratio", "Candle_Dominance",
    "Regime_Consistency_Count",
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
    "TWAP_Z_Score", "Breakout_Velocity", "Day_Of_Week",
    "ATR_Ratio", "Bollinger_Band_Width", "Dist_Synth_H4_EMA", "Dist_Synth_D1_EMA",
    "Ribbon_Compression_ATR", "Spectrum_Alignment", "Price_to_Macro_HMA_Dist", "Ribbon_Spread_StdDev"
]

# ── Features del Modelo de Salidas ───────────────────────────────────────────
# Solo información disponible en el momento exacto del amago de cierre.
# Ninguna de estas columnas es posterior al momento de la señal de salida.
EXIT_FEATURES = [
    "Bars_In_Trade",           # Duracion hasta el amago (conocida en ese momento)
    "Open_Profit_R",           # RR flotante (precio actual vs apertura)
    "Drawdown_From_Peak_R",    # Caida desde el pico MFE hasta ahora
    "Macro_ADX_Exit",          # ADX en momento de salida
    "Exit_Volatility_Ratio",   # ATR_actual / SMA50(ATR)
    "Spread_Impact_Exit",      # Impacto del spread al momento de salir
    "Is_Trigger_Fast",         # One-Hot: gatillo HMA rapida
    "Is_Trigger_Slow",         # One-Hot: gatillo HMA lenta
    "Is_Trigger_RSI",          # One-Hot: gatillo RSI 50
    "Is_Trigger_Profit",       # One-Hot: gatillo Profit Trailing
    "Is_Trigger_Fast_HMA_Cross", # Fase 12: gatillo cruce HMA rapida
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
    "Peak_HMA_Stretch_ATR", "Current_HMA_Stretch_ATR", "Elastic_Retracement_Pct"
]

# ── Features del Motor de Régimen (KMeans) ──────────────────────────────────
REGIME_FEATURES = [
    "ATR_Norm", "Bollinger_Dev", "Z_Score", "MTF_ATR_Ratio", "Macro_ADX"
]

# ── Hiperespacio del Grid Search 2D ──────────────────────────────────────────
ENTRY_THRESHOLDS = np.round(np.arange(0.10, 0.50, 0.02), 2)
EXIT_THRESHOLDS  = np.round(np.arange(0.50, 0.85, 0.05), 2)

# ── Parámetros de riesgo para el Alpha Score ──────────────────────────────────
TRADING_DAYS_YEAR = 252
MIN_TRADES        = 100       # Mínimo de trades para significancia estadística

# ── XGBoost base — parámetros robustos para series temporales ─────────────────
XGB_PARAMS = dict(
    n_estimators      = 150,     # Limitado por Early Stopping de 2 pasos
    max_depth         = 4,       # Stumps para evitar sobreajuste extremo
    learning_rate     = 0.02,    # Aprendizaje lento y estable
    gamma             = 1.5,     # Requiere reducción de pérdida masiva
    min_child_weight  = 20,      # Previene hojas ruidosas muy pequeñas
    subsample         = 0.7,
    colsample_bytree  = 0.7,
    reg_alpha         = 1.0,     # Regularización L1 (Lasso)
    reg_lambda        = 5.0,     # Regularización L2 (Ridge)
    use_label_encoder = False,
    eval_metric       = "logloss",
    random_state      = 42,
    n_jobs            = -1,
)

EXIT_XGB_PARAMS = XGB_PARAMS.copy()
EXIT_XGB_PARAMS["min_child_weight"] = 10

N_SPLITS = 5   # TimeSeriesSplit folds


# =============================================================================
# ── 1. CARGA Y VALIDACIÓN DE DATOS ────────────────────────────────────────────
# =============================================================================

def cargar_entry_dataset(entry_csv: str) -> tuple:
    print(f"\n[ENTRY DATA] Cargando: {entry_csv}")
    df = pd.read_csv(entry_csv)
    
    # --- PHASE 67: REALITY PATCH (PATH DEPENDENCY) ---
    if "MAE_ATR" in df.columns:
        MAX_SL_ATR = 5.0
        mask_stop_out = df["MAE_ATR"] <= -MAX_SL_ATR
        stop_count = mask_stop_out.sum()
        if stop_count > 0:
            print(f"  [REALITY PATCH] Corrigiendo {stop_count} operaciones por Path Dependency (Stop Loss perforado).")
            df.loc[mask_stop_out, "Realized_RR"] = -1.0
            df.loc[mask_stop_out, "Label"] = 0
    # -------------------------------------------------
    
    print(f"  Filas totales: {len(df):,}")
    print(f"  Distribución Label: {df['Label'].value_counts().to_dict()}")

    # Convertir Time a datetime y ordenar cronologicamente (Zero Look-Ahead)
    df["Time"] = pd.to_datetime(df["Time"])
    
    df = df.sort_values("Time").reset_index(drop=True)
    
    # Fase 36.5: Escalar cinemática a Puntos por Minuto
    if "Breakout_Velocity" in df.columns:
        df["Breakout_Velocity"] = df["Breakout_Velocity"] * 60.0

    # === GENERACIÓN DE TARGET BINARIO ===
    # El dataset de entradas usa triple barrera donde:
    #   Label=1  → el trade alcanzó el TP antes que el SL/tiempo
    #   Label=0  → el trade tocó el SL antes del TP/tiempo
    #   Label=-1 → el trade cerró por barrera temporal (resultado neutro/mixto)
    # Si no hay Label=1 en el dataset (TP=0 desactivado en el EA),
    # construimos el target binario desde Realized_RR:
    #   Label_ML=1 si Realized_RR >= 1.0 (Meta-Labeling estricto: ¿justifica 1R?)
    #   Label_ML=0 si Realized_RR < 1.0
    RR_POSITIVE_THRESHOLD = 1.0  # Al menos 1.0R para considerarlo bueno

    if df["Label"].eq(1).sum() == 0:
        print(f"  [INFO] Label=1 ausente. Generando target binario desde Realized_RR >= {RR_POSITIVE_THRESHOLD}")
        df_clean = df.copy()
        df_clean["Label"] = (df_clean["Realized_RR"] >= RR_POSITIVE_THRESHOLD).astype(int)
    else:
        df_clean = df[df["Label"].isin([0, 1])].copy()

    pos = df_clean["Label"].sum()
    neg = (df_clean["Label"] == 0).sum()
    print(f"  Target binario → Positivos (Label=1): {pos:,} | Negativos (Label=0): {neg:,}")
    print(f"  Balance: {pos / len(df_clean) * 100:.1f}% positivos")

    # Filtrar filas sin Realized_RR válido
    df_clean = df_clean[df_clean["Realized_RR"].notna()].copy()

    # Verificar features disponibles
    missing = [c for c in ENTRY_FEATURES if c not in df_clean.columns]
    if missing:
        print(f"  [AVISO] Features ausentes en entry dataset: {missing}")

    return df, df_clean   # raw (para merge) + limpio (para entrenamiento)


def cargar_exit_dataset(exit_csv: str) -> tuple:
    print(f"\n[EXIT DATA] Cargando: {exit_csv}")
    df = pd.read_csv(exit_csv)
    print(f"  Filas totales (exit dilemmas): {len(df):,}")
    print(f"  Distribución Label: {df['Label'].value_counts().to_dict()}")

    # Filtrar solo labels válidos
    df_clean = df[df["Label"].isin([0, 1])].copy()
    print(f"  Dilemmas válidos: {len(df_clean):,}")

    missing = [c for c in EXIT_FEATURES if c not in df_clean.columns]
    if missing:
        print(f"  [AVISO] Features ausentes en exit dataset: {missing}")

    return df, df_clean



# =============================================================================
# ── 2. MOTOR DE RÉGIMEN (K-MEANS) ─────────────────────────────────────────────
# =============================================================================

def entrenar_regime_model(df_clean, symbol: str, timestamp: str):
    import json
    import os
    import joblib
    print("\n" + "="*60)
    print("ENTRENANDO MOTOR DE RÉGIMEN (K-Means)")
    print("="*60)
    
    available_features = [c for c in REGIME_FEATURES if c in df_clean.columns]
    X_reg = df_clean[available_features].fillna(0).values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_reg)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    df_clean["Regime_Cluster"] = clusters
    
    cluster_metrics = []
    for c in range(3):
        mask = (clusters == c)
        win_rate = df_clean.loc[mask, "Label"].mean()
        avg_rr = df_clean.loc[mask, "Realized_RR"].mean()
        count = mask.sum()
        cluster_metrics.append({"cluster": c, "win_rate": win_rate, "avg_rr": avg_rr, "count": count})
        print(f"  Cluster {c}: WinRate={win_rate*100:.1f}% | AvgRR={avg_rr:.3f} | N={count}")
        
    cluster_metrics.sort(key=lambda x: x["win_rate"])
    toxic_id = int(cluster_metrics[0]["cluster"])
    print(f"  → Régimen TÓXICO identificado: Cluster {toxic_id}")
    
    scaler_path = os.path.join(OUTPUT_DIR, f"scaler_universal_{symbol}_regimen_{timestamp}.pkl")
    model_path = os.path.join(OUTPUT_DIR, f"regimen_universal_{symbol}_kmeans_{timestamp}.pkl")
    toxic_path = os.path.join(OUTPUT_DIR, f"toxic_universal_{symbol}_{timestamp}.json")
    
    joblib.dump(scaler, scaler_path)
    joblib.dump(kmeans, model_path)
    with open(toxic_path, "w") as f:
        json.dump({"toxic_id": toxic_id, "features": available_features}, f)
        
    return df_clean, toxic_id

# =============================================================================
# ── 3. ENTRENAMIENTO MODELO DE ENTRADAS (ENTRY MODEL) ─────────────────────────
# =============================================================================

def entrenar_entry_model(df_clean, toxic_id, symbol: str, timestamp: str):

    """
    Entrena un XGBClassifier sobre el dataset de entradas con validación
    temporal estricta (TimeSeriesSplit). Retorna el modelo final y las
    probabilidades OOF (Out-Of-Fold) sobre todos los datos de entrenamiento.
    """
    print("\n" + "="*60)
    print("ENTRENANDO MODELO DE ENTRADAS (Entry Model)")
    print("="*60)

    available_features = [c for c in ENTRY_FEATURES if c in df_clean.columns]
    X_raw = df_clean[available_features].values
    
    print("  [PREPROCESAMIENTO] Ajustando QuantileTransformer (Entry Model)...")
    entry_scaler = QuantileTransformer(output_distribution='uniform', random_state=42)
    X = entry_scaler.fit_transform(X_raw)
    
    scaler_entry_path = os.path.join(OUTPUT_DIR, f"scaler_universal_{symbol}_entry.pkl")
    joblib.dump(entry_scaler, scaler_entry_path)
    y = df_clean["Label"].values
    
    # Class Balancing (scale_pos_weight)
    scale_weight = np.sum(y == 0) / max(1, np.sum(y == 1))
    print(f"  [CLASS BALANCING] Inyectando scale_pos_weight = {scale_weight:.3f}")
    
    # Concept Drift Weights (Agresivo Post-2023) + Weight Winsorization (Fase 40.6)
    years = pd.to_datetime(df_clean['Time']).dt.year.values
    time_weights = np.where(years >= 2023, 2.0, np.where(years >= 2020, 1.2, 0.8))
    
    # Winsorization: Cap Realized_RR magnitude between 0.1 and 3.0 to prevent Gradient Hijacking
    if "Realized_RR" in df_clean.columns:
        rr_weights = np.clip(df_clean["Realized_RR"].abs(), 0.1, 3.0).values
        weights = time_weights * rr_weights
    else:
        weights = time_weights

    # --- FASE 40: PRE-ABLATION FEATURE SELECTION ---
    print("\n  [PRE-ABLATION] Entrenando modelo global base para Feature Selection...")
    split_idx = int(len(X) * 0.85)
    X_train_base, X_val_base = X[:split_idx], X[split_idx:]
    y_train_base, y_val_base = y[:split_idx], y[split_idx:]
    w_train_base, w_val_base = weights[:split_idx], weights[split_idx:]
    
    base_model = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight, early_stopping_rounds=20)
    base_model.fit(X_train_base, y_train_base, sample_weight=w_train_base, eval_set=[(X_val_base, y_val_base)], sample_weight_eval_set=[w_val_base], verbose=False)
    
    print("  [FEATURE ABLATION] Calculando Permutation Importance (F1 Score)...")
    sample_idx = np.random.choice(len(X), min(len(X), 5000), replace=False)
    if len(np.unique(y[sample_idx])) < 2:
        print("  [AVISO] Omitiendo Permutation Importance (solo 1 clase en la muestra).")
        importances = np.zeros(X.shape[1])
    else:
        try:
            perm_result = permutation_importance(
                base_model, X[sample_idx], y[sample_idx], scoring='f1',
                n_repeats=5, random_state=42, n_jobs=-1
            )
            importances = perm_result.importances_mean
        except Exception as e:
            print(f"  [AVISO] Falló Feature Ablation: {e}")
            importances = np.zeros(X.shape[1])
    surviving_features = []
    print("  Importancia real (OOF estimado vía permutación):")
    for i, feat in enumerate(available_features):
        imp = importances[i]
        if imp < 0.005:
            print(f"    [X] ELIMINADA: {feat} (Imp: {imp:.4f} < 0.5%)")
        else:
            print(f"    [OK] MANTENIDA: {feat} (Imp: {imp:.4f})")
            surviving_features.append(feat)
            
    if len(surviving_features) > 0:
        indices = [available_features.index(f) for f in surviving_features]
        available_features = surviving_features
        X = X[:, indices]
        print(f"\n  [PRE-ABLATION OK] Universo reducido a {len(surviving_features)} features. El pipeline usará SOLO estas features.")
    else:
        print("\n  [ADVERTENCIA] Todas las features eliminadas. Manteniendo originales.")

    # --- WHITE NOISE TEST ---
    print("\n  [WHITE NOISE TEST] Ejecutando estrés con etiquetas aleatorias (esperado: F1 ~ 0)...")
    np.random.seed(42)
    y_noise = np.random.permutation(y)
    
    n_samples_noise = len(X)
    adaptive_gap_noise = min(200, max(5, n_samples_noise // 15))
    if n_samples_noise > adaptive_gap_noise * 3:
        tscv_noise = TimeSeriesSplit(n_splits=2, gap=adaptive_gap_noise)
        noise_f1s = []
        for train_idx, val_idx in tscv_noise.split(X):
            if len(np.unique(y_noise[tr_idx := train_idx])) < 2 or len(np.unique(y_noise[val_idx])) < 2:
                continue
            model_noise = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight)
            model_noise.fit(X[train_idx], y_noise[train_idx], verbose=False)
            preds = model_noise.predict(X[val_idx])
            noise_f1s.append(f1_score(y_noise[val_idx], preds, zero_division=0))
        if noise_f1s:
            print(f"  → White Noise F1 Media: {np.mean(noise_f1s):.3f}")
        else:
            print("  → White Noise F1 Media: N/A (splits mono-clase)")
    else:
        print("  → White Noise test omitido (dataset demasiado pequeño para splits)")

    # --- FASE 40: EXPANDING WALK-FORWARD OPTIMIZATION ---
    df_clean["Time"] = pd.to_datetime(df_clean["Time"])
    min_date = df_clean["Time"].min()
    max_date = df_clean["Time"].max()
    
    start_date = min_date
    current_end = start_date + pd.DateOffset(months=60) # 5 years min history # 5 años mínima historia
    STEP_MONTHS = 6
    
    oof_proba = np.full(len(X), np.nan)
    fold = 1
    fold_metrics = []
    wfo_registry = {}
    
    print(f"\n  [WFO EXPANDING] Iniciando Walk-Forward (Anclado en {start_date.date()}, Paso={STEP_MONTHS}m)...")
    
    while True:
        oos_end = current_end + pd.DateOffset(months=STEP_MONTHS)
        if current_end >= max_date:
            break
            
        train_mask = (df_clean["Time"] >= start_date) & (df_clean["Time"] < current_end)
        oos_mask = (df_clean["Time"] >= current_end) & (df_clean["Time"] < min(oos_end, max_date))
        
        if oos_mask.sum() == 0:
            current_end += pd.DateOffset(months=STEP_MONTHS)
            continue
            
        X_tr, y_tr, w_tr = X[train_mask], y[train_mask], weights[train_mask]
        X_oos, y_oos = X[oos_mask], y[oos_mask]
        
        if len(np.unique(y_tr)) < 2:
            print(f"  [WFO] Fold {fold} omitido: No hay suficientes clases.")
            current_end += pd.DateOffset(months=STEP_MONTHS)
            continue
            
        model_base = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight)
        model = CalibratedClassifierCV(estimator=model_base, method='isotonic', cv=5)
        model.fit(pd.DataFrame(X_tr, columns=available_features), y_tr, sample_weight=w_tr)
        
        preds_proba = model.predict_proba(pd.DataFrame(X_oos, columns=available_features))[:, 1]
        oof_proba[oos_mask] = preds_proba
        
        wfo_model_name = f"wfo_entry_{symbol}_{current_end.date()}_to_{oos_end.date()}.pkl"
        wfo_model_path = os.path.join(OUTPUT_DIR, wfo_model_name)
        model.feature_names_in_ = np.array(available_features)
        model.expected_features_ = available_features
        joblib.dump(model, wfo_model_path)
        wfo_registry[str(oos_end.date())] = wfo_model_name
        
        pred_05 = (preds_proba >= 0.50).astype(int)
        p = precision_score(y_oos, pred_05, zero_division=0)
        f = f1_score(y_oos, pred_05, zero_division=0)
        fold_metrics.append({"fold": fold, "precision": p, "recall": 0, "f1": f})
        
        print(f"  [WFO] {start_date.date()}->{current_end.date()} | OOS: {min(oos_end, max_date).date()} | N={oos_mask.sum()} | Precision={p:.3f} | F1={f:.3f}")
        
        current_end += pd.DateOffset(months=STEP_MONTHS)
        fold += 1

    metrics_df = pd.DataFrame(fold_metrics)
    if not metrics_df.empty:
        print(f"\n  Media OOS — Precision: {metrics_df['precision'].mean():.3f} | F1: {metrics_df['f1'].mean():.3f}")

    import json
    registry_path = os.path.join(OUTPUT_DIR, f"wfo_registry_entry_{symbol}.json")
    with open(registry_path, "w") as f:
        json.dump(wfo_registry, f, indent=4)
    print(f"  [WFO REGISTRY] Guardado en: {registry_path}")

    toxic_mask = (df_clean["Regime_Cluster"] == toxic_id).values
    print(f"\n  [FILTRO DE RÉGIMEN] Anulando probabilidad para {toxic_mask.sum()} trades tóxicos.")
    oof_proba = np.where(toxic_mask & ~np.isnan(oof_proba), 0.0, oof_proba)

    # --- CALIBRACIÓN MODELO LIVE ---
    print("\n  [LIVE MODEL] Entrenando modelo de Producción (Expanding Global + Concept Drift)...")
    split_idx = int(len(X) * 0.85)
    X_train_cal, X_val_cal = X[:split_idx], X[split_idx:]
    y_train_cal, y_val_cal = y[:split_idx], y[split_idx:]
    w_train_cal, w_val_cal = weights[:split_idx], weights[split_idx:]

    temp_model_cal = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight, early_stopping_rounds=20)
    temp_model_cal.fit(X_train_cal, y_train_cal, sample_weight=w_train_cal, eval_set=[(X_val_cal, y_val_cal)], sample_weight_eval_set=[w_val_cal], verbose=False)
    
    optimal_trees = max(10, temp_model_cal.best_iteration)
    print(f"  → Óptimo de árboles encontrado: {optimal_trees}")

    final_params = XGB_PARAMS.copy()
    final_params["n_estimators"] = optimal_trees
    
    final_model_base = XGBClassifier(**final_params, scale_pos_weight=scale_weight)
    final_model = CalibratedClassifierCV(estimator=final_model_base, method='isotonic', cv=5)
    final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights)

    # Guardar
    model_path = os.path.join(OUTPUT_DIR, f"modelo_universal_{symbol}_entry_{timestamp}.pkl")
    final_model.feature_names_in_ = np.array(available_features)
    final_model.expected_features_ = available_features
    joblib.dump(final_model, model_path)
    print(f"  Modelo guardado en: {model_path}")

    # Retornar proba OOF para el grid search
    df_clean = df_clean.copy()
    df_clean["entry_proba"] = oof_proba

    return final_model, df_clean, available_features


# =============================================================================
# ── 3. ENTRENAMIENTO MODELO DE SALIDAS (EXIT MODEL) ───────────────────────────
# =============================================================================

def entrenar_exit_model(df_exit_clean: pd.DataFrame, symbol: str, timestamp: str):
    """
    Entrena un XGBClassifier sobre el dataset de salidas.
    Label=1: cerrar era correcto (no dejamos nada en la mesa > 1R)
    Label=0: error (debíamos haber aguantado — Missed_Profit_R > 1R)
    Zero Leakage: solo usa features disponibles en el momento del amago.
    """
    print("\n" + "="*60)
    print("ENTRENANDO MODELO DE SALIDAS (Exit Model)")
    print("="*60)

    available_features = [c for c in EXIT_FEATURES if c in df_exit_clean.columns]
    X_raw = df_exit_clean[available_features].values
    
    print("  [PREPROCESAMIENTO] Ajustando QuantileTransformer (Exit Model)...")
    exit_scaler = QuantileTransformer(output_distribution='uniform', random_state=42)
    X = exit_scaler.fit_transform(X_raw)
    
    scaler_exit_path = os.path.join(OUTPUT_DIR, f"scaler_universal_{symbol}_exit.pkl")
    joblib.dump(exit_scaler, scaler_exit_path)
    y = df_exit_clean["Label"].values
    
    scale_weight = np.sum(y == 0) / max(1, np.sum(y == 1))
    print(f"  [CLASS BALANCING] Inyectando scale_pos_weight = {scale_weight:.3f}")

    # Concept Drift Weights
    if 'Time' in df_exit_clean.columns:
        years = pd.to_datetime(df_exit_clean['Time']).dt.year.values
        weights = np.where(years >= 2022, 1.5, 0.8)
    else:
        weights = np.ones(len(df_exit_clean))  # Exit CSV no tiene Time, pesos uniformes

    # --- PURGED K-FOLD (gap adaptativo al tamaño del dataset) ---
    n_samples = len(X)
    # Gap = mínimo entre 200 y 10% del dataset, para no colapsar con datasets pequeños
    adaptive_gap = min(200, max(5, n_samples // 15))
    # N_splits adaptativo: si el dataset es muy pequeño reducimos splits
    adaptive_splits = N_SPLITS if n_samples > adaptive_gap * (N_SPLITS + 1) else max(2, n_samples // (adaptive_gap + 1) - 1)
    tscv = TimeSeriesSplit(n_splits=adaptive_splits, gap=adaptive_gap)
    oof_proba = np.zeros(len(X))

    fold_metrics = []
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]
        w_tr, w_val = weights[train_idx], weights[val_idx]

        # Guard: skip fold si el set de validación tiene solo una clase
        if len(np.unique(y_val)) < 2 or len(np.unique(y_tr)) < 2:
            print(f"  Fold {fold}: SALTADO (mono-clase en train o val)")
            fold_metrics.append({"fold": fold, "precision": 0, "recall": 0, "f1": 0})
            continue

        model_base = XGBClassifier(**EXIT_XGB_PARAMS, scale_pos_weight=scale_weight)
        model = CalibratedClassifierCV(estimator=model_base, method='isotonic', cv=5)
        model.fit(pd.DataFrame(X_tr, columns=available_features), y_tr, sample_weight=w_tr)

        proba = model.predict_proba(X_val)[:, 1]
        oof_proba[val_idx] = proba

        pred_05 = (proba >= 0.50).astype(int)
        p = precision_score(y_val, pred_05, zero_division=0)
        r = recall_score(y_val, pred_05, zero_division=0)
        f = f1_score(y_val, pred_05, zero_division=0)
        fold_metrics.append({"fold": fold, "precision": p, "recall": r, "f1": f})
        print(f"  Fold {fold}: Precision={p:.3f} | Recall={r:.3f} | F1={f:.3f}")

    metrics_df = pd.DataFrame(fold_metrics)
    print(f"\n  Media OOF — Precision: {metrics_df['precision'].mean():.3f} "
          f"| Recall: {metrics_df['recall'].mean():.3f} "
          f"| F1: {metrics_df['f1'].mean():.3f}")

    # =========================================================================
    # CALIBRACIÓN INSTITUCIONAL DEL MODELO FINAL (Two-Step Fit)
    # =========================================================================
    print("\n  [Calibración Final] Calculando límite óptimo de árboles (85/15 split)...")
    split_idx = int(len(X) * 0.85)
    X_train_cal, X_val_cal = X[:split_idx], X[split_idx:]
    y_train_cal, y_val_cal = y[:split_idx], y[split_idx:]

    # Guard: si el split de validación tiene una sola clase, el Early Stopping falla.
    # En ese caso usamos el máximo de estimadores del config directamente.
    val_classes = np.unique(y_val_cal)
    if len(val_classes) < 2:
        print("  [AVISO] Split de validación mono-clase. Usando n_estimators del config directamente.")
        optimal_trees = EXIT_XGB_PARAMS.get('n_estimators', 100)
    else:
        # Paso A (Descubrimiento): Early Stopping sobre el 15% final
        temp_model = XGBClassifier(**EXIT_XGB_PARAMS, scale_pos_weight=scale_weight, early_stopping_rounds=20)
        temp_model.fit(X_train_cal, y_train_cal, eval_set=[(X_val_cal, y_val_cal)], verbose=False)
        optimal_trees = max(10, temp_model.best_iteration)
    print(f"  → Óptimo de árboles encontrado antes del overfit: {optimal_trees}")

    # Paso B (Retrain Completo): Entrenar sobre TODO el dataset con el límite estricto
    final_params = EXIT_XGB_PARAMS.copy()
    final_params["n_estimators"] = optimal_trees
    
    print("  [Retrain Completo] Entrenando modelo definitivo sobre el 100% de los datos...")
    final_model_base = XGBClassifier(**final_params, scale_pos_weight=scale_weight)
    final_model = CalibratedClassifierCV(estimator=final_model_base, method='isotonic', cv=5)
    final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights)

    # --- PERMUTATION IMPORTANCE ---
    print("\n  [FEATURE ABLATION] Calculando Permutation Importance (F1 Score)...")
    sample_idx = np.random.choice(len(X), min(len(X), 5000), replace=False)
    if len(np.unique(y[sample_idx])) < 2:
        print("  [AVISO] Omitiendo Permutation Importance (solo 1 clase en la muestra).")
        importances = np.zeros(X.shape[1])
    else:
        try:
            perm_result = permutation_importance(
                final_model, X[sample_idx], y[sample_idx], scoring='f1',
                n_repeats=5, random_state=42, n_jobs=-1
            )
            importances = perm_result.importances_mean
        except Exception as e:
            print(f"  [AVISO] Falló Feature Ablation: {e}")
            importances = np.zeros(X.shape[1])
    surviving_features = []
    print("  Importancia real (OOF estimado vía permutación):")
    for i, feat in enumerate(available_features):
        imp = importances[i]
        if imp < 0.01:
            print(f"    [X] ELIMINADA: {feat} (Imp: {imp:.4f} < 1%)")
        else:
            print(f"    [OK] MANTENIDA: {feat} (Imp: {imp:.4f})")
            surviving_features.append(feat)
            
    if len(surviving_features) < len(available_features) and len(surviving_features) > 0:
        print(f"\n  [RETRAIN PURGADO] Re-entrenando modelo final solo con {len(surviving_features)} features sobrevivientes...")
        indices = [available_features.index(f) for f in surviving_features]
        available_features = surviving_features
        X_surv = X[:, indices]
        final_model_base = XGBClassifier(**final_params, scale_pos_weight=scale_weight)
        final_model = CalibratedClassifierCV(estimator=final_model_base, method='isotonic', cv=5)
        final_model.fit(pd.DataFrame(X_surv, columns=available_features), y, sample_weight=weights)

    model_path = os.path.join(OUTPUT_DIR, f"modelo_universal_{symbol}_exit_{timestamp}.pkl")
    final_model.feature_names_in_ = np.array(available_features)
    final_model.expected_features_ = available_features
    joblib.dump(final_model, model_path)
    print(f"  Modelo guardado en: {model_path}")

    df_exit_clean = df_exit_clean.copy()
    df_exit_clean["exit_proba"] = oof_proba

    return final_model, df_exit_clean, available_features


# =============================================================================
# ── 4. FUSIÓN RELACIONAL (JOIN POR TICKET) ────────────────────────────────────
# =============================================================================

def fusionar_datasets(
    df_entry_raw: pd.DataFrame,
    df_entry_proba: pd.DataFrame,
    df_exit_proba: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join estructurado para el backtest:

    Para cada Trade (Ticket), necesitamos:
      - entry_proba: ¿cuánta confianza tiene el Entry Model en esta entrada?
      - Realized_RR: resultado real (si ningún exit model interviene)
      - Exit dilemmas ordenados cronológicamente (Bars_In_Trade ASC):
          → El primero con exit_proba >= exit_thresh define la salida anticipada.

    Retorna df_entry enriquecido con entry_proba + todos los exit dilemmas
    por ticket como una lista ordenada (stored as columna json-like).
    El backtest vectorizado accederá a esta estructura de forma eficiente.
    """
    print("\n[MERGE] Fusionando datasets por Ticket...")

    # Añadir entry_proba al df_entry_raw (incluyendo Label=-1 para completitud)
    proba_map = df_entry_proba.set_index("Ticket")["entry_proba"].to_dict()
    df_entry_raw["entry_proba"] = df_entry_raw["Ticket"].map(proba_map)

    # Construir tabla de exit dilemmas por ticket:
    # Para cada Ticket, guardamos lista de (Bars_In_Trade, Floating_RR, exit_proba)
    # ordenada por Bars_In_Trade ASC (orden temporal de aparición del dilema)
    exit_cols_needed = ["Ticket", "Bars_In_Trade", "Open_Profit_R", "exit_proba"]
    df_ex = df_exit_proba[exit_cols_needed].copy()
    df_ex = df_ex.sort_values(["Ticket", "Bars_In_Trade"])

    # Agrupar: para cada Ticket → array de (bars, floating_rr, exit_proba)
    # Usamos groupby vectorizado y almacenamos como arrays numpy por ticket
    grp = df_ex.groupby("Ticket")
    exit_map = {
        ticket: {
            "bars":       grp_df["Bars_In_Trade"].values,
            "float_rr":   grp_df["Open_Profit_R"].values,
            "exit_proba": grp_df["exit_proba"].values,
        }
        for ticket, grp_df in grp
    }

    print(f"  Tickets en entry dataset:     {len(df_entry_raw):,}")
    print(f"  Tickets con exit dilemmas:    {len(exit_map):,}")
    joined = df_entry_raw["Ticket"].isin(exit_map).sum()
    print(f"  Tickets con join completo:    {joined:,}")
    no_exit = (~df_entry_raw["Ticket"].isin(exit_map)).sum()
    print(f"  Tickets sin exit dilemmas:    {no_exit:,} "
          f"(usarán Realized_RR directo del dataset)")

    df_entry_raw["_exit_map"] = df_entry_raw["Ticket"].map(exit_map)

    return df_entry_raw, exit_map


# =============================================================================
# ── 5. BACKTEST VECTORIZADO 2D ────────────────────────────────────────────────
# =============================================================================

def _simular_combo(
    df_entries: pd.DataFrame,
    exit_map: dict,
    entry_thresh: float,
    exit_thresh: float,
) -> dict:
    # Paso 1: filtrar por umbral de entrada
    if "entry_proba" not in df_entries.columns:
        # Sin modelo de entrada: usar todos
        df_selected = df_entries.copy()
    else:
        df_selected = df_entries[
            df_entries["entry_proba"].notna() &
            (df_entries["entry_proba"] >= entry_thresh)
        ].copy()

    n_trades = len(df_selected)
    if n_trades < MIN_TRADES:
        return {"n_trades": n_trades, "alpha_score": -np.inf,
                "sharpe": np.nan, "annual_r": np.nan, "max_dd": np.nan,
                "entry_thresh": entry_thresh, "exit_thresh": exit_thresh}

    # Paso 2: calcular el RR efectivo de cada trade
    # Para los tickets con exit dilemmas, encontrar el primer dilema que
    # supere el exit_thresh → ese Floating_RR pasa a ser el resultado.
    def get_effective_rr(row):
        ticket = row["Ticket"]
        base_rr = float(row["Realized_RR"])

        # 1. Resolver el Exit Model Trigger
        exit_model_rr = base_rr
        if ticket in exit_map:
            em = exit_map[ticket]
            mask = em["exit_proba"] >= exit_thresh
            if mask.any():
                first_idx = np.argmax(mask)
                exit_model_rr = float(em["float_rr"][first_idx])

        # 2. Sin Scale-Out: El AI Exit es absoluto.
        return exit_model_rr

    df_selected["effective_rr"] = df_selected.apply(get_effective_rr, axis=1)

    # Paso 3: construir equity curve (1% riesgo fijo por trade)
    # Cada trade contribuye con +effective_rr% × 1R o -1R
    # Usamos 1R = 1% de capital → cada trade = ±1% × effective_rr
    rr_series = df_selected["effective_rr"].values.astype(float)
    equity_pct = rr_series * 0.01   # 1% risk per trade → resultado en fracción de capital

    equity_curve = np.cumprod(1 + equity_pct)

    # Sharpe Ratio anualizado
    # Asumimos distribución uniforme de trades en el período
    mean_r   = np.mean(equity_pct)
    std_r    = np.std(equity_pct, ddof=1)
    sharpe   = 0.0 if std_r < 1e-9 else (mean_r / std_r) * np.sqrt(TRADING_DAYS_YEAR)

    # Annual Return (compuesto, normalizado al período del dataset)
    total_return = equity_curve[-1] - 1.0
    # Aproximamos días de trading: usando Bars_In_Trade suma total / TRADING_DAYS_YEAR
    n_days = df_selected["Bars_In_Trade"].sum() / 4.0   # 4 velas M15 = 1 hora, ~6.5h día
    n_years = max(n_days / TRADING_DAYS_YEAR, 0.01)
    annual_r = ((1 + total_return) ** (1 / n_years)) - 1.0

    # Max Drawdown (en porcentaje del equity)
    running_max = np.maximum.accumulate(equity_curve)
    drawdown    = (equity_curve - running_max) / running_max
    max_dd      = abs(drawdown.min()) * 100.0   # en %

    # Alpha Score institucional (Fase 35): Máximo foco en Sharpe y Calmar para aplastar Drawdown
    sign = 1 if (annual_r > 0 and sharpe > 0) else -1
    calmar_ratio = abs(annual_r) / max(max_dd, 1.0)
    alpha_score = sign * abs(sharpe) * calmar_ratio * np.log(max(n_trades, 2))

    return {
        "entry_thresh": entry_thresh,
        "exit_thresh":  exit_thresh,
        "n_trades":     n_trades,
        "sharpe":       round(sharpe, 4),
        "annual_r":     round(annual_r * 100, 2),   # en %
        "max_dd":       round(max_dd, 2),            # en %
        "win_rate":     round((rr_series > 0).mean() * 100, 2),
        "avg_rr":       round(np.mean(rr_series), 4),
        "alpha_score":  round(alpha_score, 4),
    }


def optimizar_hiperespacio(
    df_entries: pd.DataFrame,
    exit_map: dict,
) -> pd.DataFrame:
    print("\n" + "="*60)
    print("OPTIMIZACIÓN BIDIMENSIONAL DEL HIPERESPACIO")
    print(f"  Entry thresholds: {list(ENTRY_THRESHOLDS)}")
    print(f"  Exit thresholds:  {list(EXIT_THRESHOLDS)}")
    combos = list(itertools.product(ENTRY_THRESHOLDS, EXIT_THRESHOLDS))
    print(f"  Total combinaciones: {len(combos)}")
    print("="*60)

    t0 = time.time()
    results = []
    for i, (et, xt) in enumerate(combos):
        r = _simular_combo(df_entries, exit_map, float(et), float(xt))
        results.append(r)
        if (i + 1) % 18 == 0:
            elapsed = time.time() - t0
            print(f"  [{i+1}/{len(combos)}] Completados... ({elapsed:.1f}s)")

    elapsed_total = time.time() - t0
    print(f"\n  Optimización completada en {elapsed_total:.1f}s")

    df_results = pd.DataFrame(results)
    df_results = df_results[df_results["n_trades"] >= MIN_TRADES]
    df_results = df_results.sort_values("alpha_score", ascending=False).reset_index(drop=True)

    return df_results


# =============================================================================
# ── 6. SELECCIÓN DE PERFILES Y REPORTE ────────────────────────────────────────
# =============================================================================

def seleccionar_perfiles(df_results: pd.DataFrame) -> dict:
    """
    Extrae los 3 perfiles institucionales del ranking:
      A — Agresivo:     Máximo Alpha Score puro (más operaciones, más riesgo)
      B — Balanceado:   Mejor Sharpe Ratio (sin importar número de trades)
      C — Conservador:  Mínimo Max Drawdown con Alpha_Score > percentil 25
    """
    print("\n" + "="*60)
    print("SELECCIÓN DE PERFILES INSTITUCIONALES")
    print("="*60)

    profiles = {}

    # Perfil A: Máximo Alpha Score
    profiles["A_Agresivo"] = df_results.iloc[0].to_dict()

    # Perfil B: Mejor Sharpe Ratio
    best_sharpe_idx = df_results["sharpe"].idxmax()
    profiles["B_Balanceado"] = df_results.loc[best_sharpe_idx].to_dict()

    # Perfil C: Mínimo Max Drawdown (con Alpha decente)
    alpha_p25 = df_results["alpha_score"].quantile(0.25)
    df_stable = df_results[df_results["alpha_score"] >= alpha_p25]
    if len(df_stable) > 0:
        min_dd_idx = df_stable["max_dd"].idxmin()
        profiles["C_Conservador"] = df_stable.loc[min_dd_idx].to_dict()
    else:
        profiles["C_Conservador"] = df_results.iloc[-1].to_dict()

    for nombre, p in profiles.items():
        print(f"\n  ── Perfil {nombre} ──────────────────────")
        print(f"     Entry Threshold : {p['entry_thresh']:.2f}")
        print(f"     Exit Threshold  : {p['exit_thresh']:.2f}")
        print(f"     N Trades        : {p['n_trades']}")
        print(f"     Sharpe          : {p['sharpe']:.4f}")
        print(f"     Annual Return   : {p['annual_r']:.2f}%")
        print(f"     Max Drawdown    : {p['max_dd']:.2f}%")
        print(f"     Win Rate        : {p['win_rate']:.2f}%")
        print(f"     Avg RR          : {p['avg_rr']:.4f}")
        print(f"     ★ Alpha Score   : {p['alpha_score']:.4f}")

    return profiles


# =============================================================================
# ── 7. HEATMAP DE ALPHA SCORE (VISUALIZACIÓN OPCIONAL) ───────────────────────
# =============================================================================

def generar_heatmap(df_results: pd.DataFrame, symbol: str, timestamp: str):
    """Genera un heatmap 2D del Alpha Score si matplotlib está disponible."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors

        pivot = df_results.pivot_table(
            values="alpha_score",
            index="exit_thresh",
            columns="entry_thresh",
            aggfunc="mean"
        )

        fig, ax = plt.subplots(figsize=(12, 7))
        vmin_val = pivot.values.min()
        vmax_val = pivot.values.max()
        # TwoSlopeNorm requiere vmin < vcenter < vmax estrictamente
        if vmin_val < 0 < vmax_val:
            divnorm = mcolors.TwoSlopeNorm(vmin=vmin_val, vcenter=0, vmax=vmax_val)
        else:
            divnorm = mcolors.Normalize(vmin=vmin_val, vmax=vmax_val)
        im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", norm=divnorm,
                       origin="lower")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{v:.2f}" for v in pivot.columns], rotation=45)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([f"{v:.2f}" for v in pivot.index])
        ax.set_xlabel("Entry Threshold", fontsize=12)
        ax.set_ylabel("Exit Threshold",  fontsize=12)
        ax.set_title(f"Alpha Score Heatmap — {symbol}\n"
                     f"Alpha = (Sharpe × Annual_R) / (MaxDD + 0.1)",
                     fontsize=13, fontweight="bold")
        plt.colorbar(im, ax=ax, label="Alpha Score")
        plt.tight_layout()

        heatmap_path = os.path.join(OUTPUT_DIR, f"alpha_heatmap_{symbol}_{timestamp}.png")
        plt.savefig(heatmap_path, dpi=150, bbox_inches="tight")
        print(f"\n  [HEATMAP] Guardado en: {heatmap_path}")
        plt.close()

    except ImportError:
        print("\n  [AVISO] matplotlib no disponible. Heatmap omitido.")

# =============================================================================
# ── 8. GUARDAR RESULTADOS Y UMBRALES PARA PRODUCCIÓN ─────────────────────────
# =============================================================================

def guardar_resultados(df_results: pd.DataFrame, profiles: dict, symbol: str, timestamp: str):
    """
    Serializa:
      - El ranking completo del Grid Search (CSV)
      - Los umbrales de producción por perfil (JSON legible por Flask/MQL5)
    """
    ranking_path = os.path.join(OUTPUT_DIR, f"grid_search_ranking_{symbol}_{timestamp}.csv")
    df_results.to_csv(ranking_path, index=False)
    print(f"\n[OUTPUT] Ranking completo guardado en: {ranking_path}")

    import json
    profiles_path = os.path.join(OUTPUT_DIR, f"umbrales_universales_{symbol}_{timestamp}.json")
    # Convertir numpy types a python nativas para JSON
    profiles_clean = {
        k: {kk: (float(vv) if isinstance(vv, (np.floating, np.integer)) else vv)
            for kk, vv in v.items()}
        for k, v in profiles.items()
    }
    with open(profiles_path, "w") as f:
        json.dump(profiles_clean, f, indent=2)
    print(f"[OUTPUT] Umbrales de producción guardados en: {profiles_path}")
    print("\n  ► Integración MQL5: usa los valores de 'entry_thresh' y")
    print("    'exit_thresh' del perfil elegido como inputs del EA.")


# =============================================================================
# ── MAIN ───────────────────────────────────────────────────────────────────────
# =============================================================================

def main():
    print("=" * 70)
    print(" HMA META-LABELING — PIPELINE GLOBAL OPTIMIZER (Fase 7)")
    print("=" * 70)

    t_total = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    import glob
    import gc
    
    parser = argparse.ArgumentParser(description="HMA Meta-Labeling Global Optimizer")
    parser.add_argument('--suffix', type=str, default='', help="Sufijo dataset (ej. _T2, _T3)")
    parser.add_argument('--symbols', type=str, default="EURUSD,GBPUSD,USDJPY,EURJPY,XAUUSD", help="Coma separados")
    args, unknown = parser.parse_known_args()
    
    assets = [s.strip() for s in args.symbols.split(",")]
    
    csv_files = [os.path.join(DATA_DIR, f"Struct_Dataset_{a}{args.suffix}.csv") for a in assets]
    
    all_portfolio_trades = []
    
    if len(csv_files) == 0:
        print("[ERROR] No se encontraron archivos Struct_Dataset_*.csv")
    else:
        # Usar bucle for y bloque condicional, sin break/continue/pass
        for file_path in csv_files:
            base_name = os.path.basename(file_path)
            symbol = base_name.replace("Struct_Dataset_", "").replace(f"{args.suffix}.csv", "").replace(".csv", "").upper()
            exit_file_path = os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{symbol}{args.suffix}.csv")
            
            if os.path.exists(exit_file_path):
                print(f"\n{'-'*70}")
                print(f" PROCESANDO ACTIVO: {symbol}")
                print(f"{'-'*70}")
                
                # Forzar recolección de basura ANTES de la carga del activo
                gc.collect()
                
                # 1. Cargar datos
                df_entry_raw, df_entry_clean = cargar_entry_dataset(file_path)
                df_exit_raw, df_exit_clean   = cargar_exit_dataset(exit_file_path)

                # 2. Motor de Régimen
                df_entry_clean, toxic_id = entrenar_regime_model(df_entry_clean, symbol, timestamp)

                # 3. Entrenar Entry Model
                entry_model, df_entry_proba, entry_feats = entrenar_entry_model(df_entry_clean, toxic_id, symbol, timestamp)

                # 4. Entrenar Exit Model
                exit_model, df_exit_proba, exit_feats = entrenar_exit_model(df_exit_clean, symbol, timestamp)

                # Fusionar datasets por Ticket
                df_merged, exit_map = fusionar_datasets(df_entry_raw, df_entry_proba, df_exit_proba)
                
                # GUARDAR DF_MERGED PARA AUDITORIA DE PORTAFOLIO
                df_merged['Symbol'] = symbol
                df_merged.to_csv(os.path.join(DATA_DIR, f"df_merged_{symbol}.csv"), index=False)

                # 5. Backtest vectorizado 2D
                df_results = optimizar_hiperespacio(df_merged, exit_map)

                print(f"\n  Combinaciones validas (>={MIN_TRADES} trades): {len(df_results)}")
                
                if len(df_results) > 0:
                    print("\n  TOP 5 por Alpha Score:")
                    print(df_results.head(5).to_string(index=False))

                    # 6. Seleccionar perfiles
                    profiles = seleccionar_perfiles(df_results)

                    # 7. Heatmap
                    generar_heatmap(df_results, symbol, timestamp)

                    # 8. Guardar resultados
                    guardar_resultados(df_results, profiles, symbol, timestamp)
                    
                    # --- EXTRAER TRADES OPTIMOS PARA PORTFOLIO ---
                    best_et = profiles['B_Balanceado']['entry_thresh']
                    best_xt = profiles['B_Balanceado']['exit_thresh']
                    
                    # Hack temporal en _simular_combo para retornar DF
                    df_selected = df_merged[df_merged["entry_proba"] >= best_et].copy()
                    
                    def get_effective_rr(row):
                        ticket = row["Ticket"]
                        base_rr = float(row["Realized_RR"])
                        exit_model_rr = base_rr
                        if ticket in exit_map:
                            em = exit_map[ticket]
                            mask = em["exit_proba"] >= best_xt
                            if mask.any():
                                first_idx = np.argmax(mask)
                                exit_model_rr = float(em["float_rr"][first_idx])
                        hit_scale_out = False
                        if exit_model_rr >= 1.5 or base_rr >= 1.5:
                            hit_scale_out = True
                        if hit_scale_out:
                            if base_rr > exit_model_rr:
                                return base_rr
                            return exit_model_rr
                        return exit_model_rr
                    
                    if not df_selected.empty:
                        df_selected["Final_RR"] = df_selected.apply(get_effective_rr, axis=1)
                        df_selected["Symbol"] = symbol
                        cols = ["Symbol", "Ticket", "Time", "Final_RR"]
                        if "Time" in df_selected.columns:
                            all_portfolio_trades.append(df_selected[cols])
                    # ---------------------------------------------

                    # 9. Dynamic Threshold Evaluation (Walk-Forward)
                    if 'Time' in df_entry_proba.columns:
                        df_entry_proba['Time'] = pd.to_datetime(df_entry_proba['Time'])
                        recent_data = df_entry_proba[df_entry_proba['Time'].dt.year >= 2025]
                        if not recent_data.empty:
                            q75 = recent_data['entry_proba'].quantile(0.75)
                            rec_thresh = profiles.get('B_Balanceado', profiles.get('A_Agresivo', {})).get('entry_thresh', 0.34)
                            print("\n" + "="*70)
                            print(" EVALUACION DINAMICA DE UMBRAL (REGIMEN OOD)")
                            print("="*70)
                            print(f"  Umbral Estatico (Grid Search) : {rec_thresh}")
                            print(f"  Percentil 75% (Post-2024)     : {q75:.4f}")
                            if q75 < rec_thresh:
                                print(f"  [ALERTA OOD] El régimen actual está comprimiendo las probabilidades.")
                                print(f"  [RECOMENDACION] Bajar EntryThreshold a {max(0.15, round(q75, 2))} para desatascar parálisis operativa.")
                            else:
                                print(f"  [OK] El régimen actual soporta el umbral estricto institucional.")
                            print("="*70)
                else:
                    print(f"\n[ERROR] No valid combinations found for {symbol}.")
                
                # Purgado de Memoria (Limpieza explícita de DataFrames)
                del df_entry_raw
                del df_entry_clean
                del df_exit_raw
                del df_exit_clean
                del df_entry_proba
                del df_exit_proba
                del df_merged
                del entry_model
                del exit_model
                gc.collect()
            else:
                print(f"[AVISO] Omitiendo {symbol}: No se encontro {exit_file_path}")
        # FINAL: Guardar la simulacion de todos los activos combinados
        if len(all_portfolio_trades) > 0:
            df_port = pd.concat(all_portfolio_trades, ignore_index=True)
            df_port.to_csv(os.path.join(DATA_DIR, 'portfolio_trades_log.csv'), index=False)
            print(f'\n[PORTFOLIO] {len(df_port)} trades exportados a portfolio_trades_log.csv')

    print('\n' + '='*70)
    print('  Pipeline global completado')
    print('='*70)

if __name__ == '__main__':
    main()

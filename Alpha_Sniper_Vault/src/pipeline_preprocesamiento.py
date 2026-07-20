# =============================================================================
# pipeline_preprocesamiento.py — HMA Meta-Labeling System
# Fase 1: Ingeniería de Datos, Rich Labeling y Preprocesamiento
# Referencia teórica: López de Prado, AFML, Caps. 3-4
# =============================================================================
# FILOSOFÍA:
#   Este módulo transforma el CSV crudo de MQL5 en un dataset listo para ML.
#   Toda la lógica de limpieza y etiquetado está encapsulada en funciones
#   puras y deterministas — sin aleatoriedad, sin dependencias de red.
# =============================================================================

import os
import sys
import io

# Forzar salida UTF-8 en terminales Windows (evita cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
import joblib

# ── Configuracion Base ────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR     = os.path.join(BASE_DIR, "output")

ACTIVO = sys.argv[1].lower() if len(sys.argv) > 1 else "gbpusd"
DATA_PATH   = os.path.join(BASE_DIR, "data", f"Struct_Dataset_{ACTIVO.upper()}.csv")
SCALER_PATH = os.path.join(OUT_DIR, f"robust_scaler_{ACTIVO}.pkl")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Anatomía canónica del dataset ──────────────────────────────────────────
FEATURE_COLS = [
    "Z_Score",        # Posición estadística del precio vs SMA20 (en σ)
    "ATR_Norm",       # Volatilidad relativa: ATR_actual / ATR_medio_10p
    "RSI",            # Momentum en la barra del cruce (Wilder 14p)
    "RSI_Extreme",    # RSI mínimo/máximo en la ventana de lookback
    "Bars_Since_Ext", # Latencia entre el extremo RSI y el cruce (velas)
    "HMA_Slope_Pct",  # 1ª derivada de HMA: inercia direccional
    "HMA_Accel",      # 2ª derivada de HMA: ¿la inercia crece o se agota?
    "Trend_Align",    # Contexto macro: +1=a favor, -1=contra-tendencia
    "Dist_Macro_EMA", # (Close - EMA200_H4) / ATR: tensión elástica macro
    "Pullback_Dur",   # Velas que el precio pasó al otro lado de la HMA
    "Pullback_Depth_Pct", # Profundidad máx. del pullback en múltiplos de ATR
    "Breakout_Force_ATR", # |Close - HMA| / ATR: fuerza de ruptura normalizada
    "SL_Dist_ATR",    # Distancia al Stop Loss en múltiplos de ATR
    "Spread_Pips",    # Spread en pips (microestructura de liquidez)
    "SL_Pips_Reales", # Distancia SL ajustada a volatilidad actual
    "Hour",           # Hora del servidor 0-23 (estacionalidad intradía)
    "Session_Time",   # Contexto estacional de sesión de trading (legítimo)
    "H4_Trend_Align", # Contexto de alineamiento de tendencia macro H4 (legítimo)
    "Vol_Spread_Ratio",# Contexto de volumen relativo a spread (legítimo)
    "ATR_Ratio_High",      # Volatilidad Relativa Extrema (ATR14 / ATR200)
    "RSI_Slope_10",        # Divergencia de momento (Cambio RSI 10 velas)
    "Spread_Impact_Ratio", # Métrica de Fricción de Costes (Spread / SL Pips)
    "HMA_Distance_EMA",    # Geometría HMA (Distancia a EMA200 en pips)
    "Breakout_Body_Ratio", # Fuerza del Bloque de Ruptura (Body / Range)
    "Day_Of_Week",         # Estacionalidad semanal (1-5)
    "HMA_Velocity",        # Cinemática: Raw 1st derivative de HMA
    "HMA_Acceleration",    # Cinemática: Raw 2nd derivative de HMA
    "HMA_Jerk",            # Cinemática: 3rd derivative (shock estructural)
    "Energy_Accumulation", # Velas consecutivas en lado opuesto antes del cruce
]

META_COLS   = ["Ticket", "Signal"]
TARGET_COLS = ["Bars_In_Trade", "MAE_Pct", "MFE_Pct", "Realized_RR", "Return_Pct", "Label"]
ALL_COLS    = META_COLS + FEATURE_COLS + TARGET_COLS

# =============================================================================
# ARCHITECTURE NOTE:
# The secondary model no longer relies on 'Label_AI' with a MAE filter.
# The target is dynamically created in pipeline_multi_activo.py using 'Realized_RR'.
# =============================================================================
# =============================================================================
# PASO 1 — CARGA DE DATOS
# =============================================================================
def cargar_dataset(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Carga el CSV de MQL5. Detecta automáticamente el separador (TAB o coma).
    Convierte la columna 'Time' a DatetimeIndex ordenado cronológicamente.
    """
    print(f"[CARGA] Leyendo: {path}")

    # MQL5 FileWrite(CSV) usa TAB por defecto; algunos brokers/locales usan coma
    df = pd.read_csv(path, sep="\t", header=0, low_memory=False)
    if df.shape[1] == 1:                        # Falló con TAB → intentar coma
        df = pd.read_csv(path, sep=",", header=0, low_memory=False)

    df.columns = df.columns.str.strip()

    # Soporte bidireccional y robusto para datasets legacy / nuevos
    if "Max_RR_Achieved" in df.columns and "Realized_RR" not in df.columns:
        print("[WARN] Dataset legacy detectado. Mapeando 'Max_RR_Achieved' a 'Realized_RR'.")
        df["Realized_RR"] = df["Max_RR_Achieved"]
    elif "Realized_RR" in df.columns and "Max_RR_Achieved" not in df.columns:
        print("[INFO] Dataset nuevo detectado. Mapeando 'Realized_RR' a 'Max_RR_Achieved' para compatibilidad.")
        df["Max_RR_Achieved"] = df["Realized_RR"]

    # Validar columnas críticas indispensables para el pipeline
    req_cols = ["Time"] + META_COLS + TARGET_COLS
    faltantes_criticas = [c for c in req_cols if c not in df.columns and c != "Time"]
    if "Time" not in df.columns and df.index.name != "Time":
        faltantes_criticas.append("Time")
    if faltantes_criticas:
        raise ValueError(
            f"[ERROR] Columnas criticas ausentes en el CSV: {faltantes_criticas}\n"
            f"Columnas recibidas: {list(df.columns)}"
        )

    # Filtrar FEATURE_COLS dinámicamente según lo que esté presente en el CSV
    global FEATURE_COLS
    present_features = [c for c in FEATURE_COLS if c in df.columns]
    ausentes_features = [c for c in FEATURE_COLS if c not in df.columns]
    if ausentes_features:
        print(f"[WARN] Features canonicas ausentes en el CSV (se omitiran del escalado): {ausentes_features}")
    if not present_features:
        raise ValueError("[ERROR] No se detectaron features validas en el CSV.")
    
    FEATURE_COLS = present_features

    # Parsear y establecer índice temporal
    df["Time"] = pd.to_datetime(df["Time"], format="%Y.%m.%d %H:%M:%S",
                                errors="coerce")
    df = df.sort_values("Time").set_index("Time")
    df.index.name = "Time"

    print(f"  → {len(df):,} señales | {df.index.min()} → {df.index.max()}")
    print(f"  → Distribución Label primario:\n{df['Label'].value_counts()}\n")
    return df


# =============================================================================
# PASO 2 — LIMPIEZA DE ANOMALÍAS (NaN / Inf de cálculos MQL5)
# =============================================================================
def limpiar_anomalias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata valores patológicos generados por divisiones por cero o buffers
    vacíos en los cálculos de punto flotante de MQL5.

    Estrategia:
      - Targets corruptos (NaN/Inf) → eliminar la fila (no recuperable).
      - Features X con NaN → imputar con la mediana de la columna.
        La mediana es resistente a outliers, a diferencia de la media.
    """
    df = df.copy()
    n_orig = len(df)

    # Infinitos → NaN para tratamiento uniforme
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Eliminar filas con cualquier target corrupto
    df.dropna(subset=["Label", "Return_Pct", "MAE_Pct", "MFE_Pct"],
              inplace=True)

    # Imputar features con mediana (estacionaria y robusta)
    for col in FEATURE_COLS:
        n_nan = df[col].isna().sum()
        if n_nan > 0:
            mediana = df[col].median()
            df[col].fillna(mediana, inplace=True)
            print(f"  [NaN] '{col}': {n_nan} valores → mediana ({mediana:.4f})")

    # Coercionar a numérico por si hay artefactos de texto
    for col in FEATURE_COLS + TARGET_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_drop = n_orig - len(df)
    print(f"[LIMPIEZA] Filas eliminadas: {n_drop:,} | Filas finales: {len(df):,}\n")
    return df


# =============================================================================
# PASO 3 — PURGA DE RESIDUOS (Zero Trust)
# =============================================================================
def purgar_residuos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Eliminamos cualquier artefacto antiguo que pueda causar confusión o Data Leakage.
    """
    df = df.copy()
    
    # Aseguramos que Label_AI no se propague si viene del CSV
    if "Label_AI" in df.columns:
        df.drop(columns=["Label_AI"], inplace=True)
        print("[RICH LABELING] Columna legacy 'Label_AI' purgada.")
        
    return df


# =============================================================================
# PASO 4 — ESCALADO CON RobustScaler
# =============================================================================
def escalar_features(df: pd.DataFrame,
                     fit: bool = True,
                     scaler_path: str = SCALER_PATH):
    """
    Escala ÚNICAMENTE las Features X continuas con RobustScaler.

    POR QUÉ RobustScaler (no StandardScaler):
      Los mercados financieros generan outliers estructurales (eventos de cola,
      noticias macro, gaps de apertura). StandardScaler amplifica estos eventos
      porque usa media y desviación estándar, ambas no robustas. RobustScaler
      usa mediana e IQR, estadísticos que ignoran los extremos y preservan la
      distribución central de los datos normales.

    AVISO ANTI-LEAKAGE:
      Cuando fit=True, el scaler se ajusta con el dataset completo. Esto es
      válido para una exploración inicial. En producción, el fit DEBE realizarse
      solo con el fold de entrenamiento dentro del loop TimeSeriesSplit.
      El módulo de entrenamiento gestiona esto correctamente.

    Returns:
        df_scaled: DataFrame con features escaladas.
        scaler:    Instancia RobustScaler ajustada (serializada en disco).
    """
    df = df.copy()

    if fit:
        scaler = RobustScaler()
        df[FEATURE_COLS] = scaler.fit_transform(df[FEATURE_COLS])
        joblib.dump(scaler, scaler_path)
        print(f"[ESCALADO] RobustScaler ajustado y guardado en: {scaler_path}")
    else:
        scaler = joblib.load(scaler_path)
        df[FEATURE_COLS] = scaler.transform(df[FEATURE_COLS])
        print(f"[ESCALADO] RobustScaler cargado desde: {scaler_path}")

    print(f"  → Features escaladas: {len(FEATURE_COLS)} columnas\n")
    return df, scaler


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar_pipeline() -> pd.DataFrame:
    """
    Orquesta los 4 pasos en el orden correcto y serializa el resultado.

    Returns:
        df: Dataset procesado, etiquetado y escalado. Listo para entrenamiento.
    """
    print("=" * 65)
    print("  HMA META-LABELING — PIPELINE DE PREPROCESAMIENTO")
    print("=" * 65 + "\n")

    df = cargar_dataset()
    df = limpiar_anomalias(df)
    df = purgar_residuos(df)
    df, _ = escalar_features(df, fit=True)

    out_path = os.path.join(OUT_DIR, f"dataset_procesado_{ACTIVO}.csv")
    df.to_csv(out_path)
    print(f"[SALIDA] Dataset procesado: {out_path}")
    print(f"  → Shape final: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    print("\n[ESTADÍSTICAS POST-ESCALADO]:")
    print(df[FEATURE_COLS].describe().round(3).to_string())
    print("\n[OK] Pipeline completado.\n")
    return df


if __name__ == "__main__":
    ejecutar_pipeline()

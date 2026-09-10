# =============================================================================
# pipeline_multi_activo.py — HMA Meta-Labeling System
# Fase 6: Automatizacion Multi-Activo (Portfolio Management)
# =============================================================================
# REFACTORING v2: Extraccion Dinamica de Features via LEAKAGE_COLS
#   - Elimina lista estatica FEATURES_ACTIVAS (9 features limitadas)
#   - Detecta las features de entrada restando columnas post-trade
#   - Soporta AUDCAD (17 features) y GBPUSD/USDJPY (20 features)
#   - Reemplaza bucle interactivo por argumento --profile (A/B/C)
# =============================================================================

import os
import sys
import io

# Forzar salida UTF-8 en terminales Windows (evita cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import warnings
import numpy as np
import pandas as pd
import joblib
import json
import glob

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_score
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Parametros del Experimento ────────────────────────────────────────────────
MODO_SCAN = "--scan" in sys.argv
if not MODO_SCAN:
    ACTIVO = sys.argv[1].lower() if len(sys.argv) > 1 else "gbpusd"
else:
    ACTIVO = "GLOBAL_SCAN"

# Seleccion de perfil via CLI: --profile A|B|C  (default: C = Hibrido)
_profile_args = [a for a in sys.argv if a.startswith("--profile")]
PERFIL_SELECCIONADO = _profile_args[0].split("=")[-1].upper() if _profile_args else (
    sys.argv[3].upper() if len(sys.argv) > 3 and sys.argv[2] == "--profile" else "C"
)
# Fallback limpio: si el argumento viene como --profile C (dos tokens separados)
if len(sys.argv) > 3 and sys.argv[2] == "--profile":
    PERFIL_SELECCIONADO = sys.argv[3].upper()
elif len(sys.argv) > 2 and sys.argv[2].startswith("--profile="):
    PERFIL_SELECCIONADO = sys.argv[2].split("=")[-1].upper()
elif "--profile" in sys.argv:
    idx = sys.argv.index("--profile")
    PERFIL_SELECCIONADO = sys.argv[idx + 1].upper() if idx + 1 < len(sys.argv) else "C"
else:
    PERFIL_SELECCIONADO = "C"

RR_GRID    = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
N_SPLITS   = 5

# ── Columnas post-trade (Data Leakage) que NUNCA son features de entrada ──────
# Extraccion dinamica: features = todas las columnas del CSV - LEAKAGE_COLS
LEAKAGE_COLS = [
    # -- Columnas post-trade directas (NUNCA features de entrada) ---------------
    "Symbol", "Ticket", "Time", "Signal_Type", "Entry_Price", "MFE_Pct", "MAE_Pct",
    "MAE_ATR", "MFE_ATR",
    "Max_RR_Achieved", "Realized_RR", "Close_Reason", "Profit_Pips", "Label",
    "Exact_Return_Pct", "Return_Pct", "Target", "y_real", "prob_ia", "retorno_r",
    # -- PURGA FORENSE DEFINITIVA (Zero-Trust) -- auditoria_antigravity v1 ------
    # Confirmado: ablacion PF 6.02 -> 0.96 al eliminar. Son post-trade o proxy.
    "Bars_In_Trade",   # POST-TRADE CRITICO: duracion del trade (corr=+0.584 con target)
    "Balance_Momento", # CONTAMINADA: equity actual codifica historial de P&L
    "Lots_Utilizados", # CONTAMINADA: lote calculado sobre equity actual
    # -- REHABILITADAS como pre-trade legitimas ---------------------------------
    # "Signal"      => PRE-TRADE: direccion BUY/SELL en apertura (ACTIVA)
    # "Pullback_Dur" => PRE-TRADE: duracion de estructura previa  (ACTIVA)
]


# =============================================================================
# FUNCIONES NUCLEO
# =============================================================================
def calcular_max_drawdown(equity_curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(equity_curve)
    dd = peak - equity_curve
    return float(dd.max()) if len(dd) > 0 else 0.0


def cargar_dataset(activo: str) -> tuple:
    """
    Carga el CSV, realiza re-labeling sintetico MFE y detecta las features
    de entrada de forma dinamica (elimina LEAKAGE_COLS del dataset).

    Returns:
        (df_limpio, lista_features) o (None, None) si hay error.
    """
    filename = f"Struct_Dataset_{activo.upper()}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"[WARN] No se encontro datos para {activo.upper()} en {filepath}")
        return None, None

    # Leer CSV, auto-detectando separador
    df = pd.read_csv(filepath, sep="\t", header=0, low_memory=False)
    if df.shape[1] == 1:
        df = pd.read_csv(filepath, sep=",", header=0, low_memory=False)

    df.columns = df.columns.str.strip()

    # Validar formato de tiempo y fijar como indice
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"], errors='coerce')
        df = df.dropna(subset=["Time"])
        df.set_index("Time", inplace=True)

    # Soporte bidireccional y robusto para datasets legacy / nuevos
    if "Max_RR_Achieved" in df.columns and "Realized_RR" not in df.columns:
        print(f"[WARN] {activo.upper()}: Dataset legacy detectado. Mapeando 'Max_RR_Achieved' a 'Realized_RR'.")
        df["Realized_RR"] = df["Max_RR_Achieved"]
    elif "Realized_RR" in df.columns and "Max_RR_Achieved" not in df.columns:
        df["Max_RR_Achieved"] = df["Realized_RR"]

    # Validar columna de objetivo
    if "Realized_RR" not in df.columns:
        print(f"[ERROR] 'Realized_RR' no encontrada en {activo.upper()}")
        return None, None

    # Deteccion dinamica de features: todas las columnas - LEAKAGE_COLS
    features = [c for c in df.columns if c not in LEAKAGE_COLS]

    if not features:
        print(f"[ERROR] No se detectaron features validas para {activo.upper()}")
        return None, None

    # Limpiar NA/Inf de forma matricial ANTES de separar Features y Target
    # Esto garantiza que los indices Pandas sean inviolables (sin Off-by-One)
    cols_a_limpiar = features + ["Realized_RR"]
    cols_existentes = [c for c in cols_a_limpiar if c in df.columns]
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=cols_existentes)

    return df, features


def entrenar_evaluar_oos(df: pd.DataFrame, features: list, anos_datos: float) -> tuple:
    """
    Entrena XGBoost con TimeSeriesSplit prediciendo si el cierre dinámico por HMA
    generará un Realized_RR >= 0.5R.
    """
    X = df[features]
    
    # PROTOCOLO V12: Net Profit Meta-Labeling
    synthetic_friction_pips = 2.5
    y = (df["Profit_Pips"] - synthetic_friction_pips > 0).astype(int)

    tss = TimeSeriesSplit(n_splits=N_SPLITS)
    probs = np.full(len(X), np.nan)
    
    for train_idx, val_idx in tss.split(X):
        X_train_raw, X_val_raw = X.iloc[train_idx], X.iloc[val_idx]
        y_train = y.iloc[train_idx]

        # Sample Weighting: proporcional a la magnitud del Realized_RR
        rr_train = df.iloc[train_idx]["Realized_RR"].values
        weights = np.clip(np.abs(rr_train), 0.1, None)
        weights = weights / weights.mean()  # Normalizar a media=1

        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc = scaler.transform(X_val_raw)

        modelo = XGBClassifier(
            max_depth=3, learning_rate=0.02, n_estimators=300,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=2.0, reg_lambda=5.0,
            eval_metric="logloss", tree_method="hist",
            early_stopping_rounds=30,
            random_state=42, n_jobs=-1, verbosity=0
        )
        modelo.fit(X_train_sc, y_train,
                   sample_weight=weights,
                   eval_set=[(X_val_sc, y.iloc[val_idx])],
                   verbose=False)
        probs[val_idx] = modelo.predict_proba(X_val_sc)[:, 1]

    # Escanear umbrales
    validos = ~np.isnan(probs)
    y_valid = y[validos]
    probs_valid = probs[validos]
    df_valid = df.iloc[validos]

    umbrales = np.arange(0.35, 0.61, 0.01)
    resultados_globales = []

    def evaluar_umbral(umbral):
        y_pred = (probs_valid >= umbral).astype(int)
        idx_aprobadas = np.where(y_pred == 1)[0]
        n_ops = len(idx_aprobadas)

        if n_ops <= 10 or anos_datos <= 0:
            return None

        y_real_aprobadas = y_valid.iloc[idx_aprobadas].values
        df_aprobadas = df_valid.iloc[idx_aprobadas]

        # Calculo de friccion dinamica
        if "Spread_Pips" in df.columns and "SL_Pips_Reales" in df.columns:
            friccion = df_aprobadas["Spread_Pips"] / df_aprobadas["SL_Pips_Reales"]
            friccion_capada = np.clip(friccion, 0.0, 0.5)
            penalty = -1.0 - friccion_capada.values
        else:
            penalty = np.full(n_ops, -1.0)

        # Retorno real = Realized_RR si ganancia, si no, perdida maxima 1R (con slippage/spread penalizado)
        # En Trend Following real, los trades negativos se asumen que salen por SL o dinámico (lo que sea peor)
        rr_aprobados = df_aprobadas["Realized_RR"].values
        retornos = np.where(rr_aprobados > 0, rr_aprobados, np.minimum(rr_aprobados, penalty))
        
        equity = np.cumsum(np.concatenate([[0], retornos]))

        prec = (retornos > 0).mean()
        ops_anuales = n_ops / anos_datos
        expectancy = retornos.mean()
        annual_r = expectancy * ops_anuales

        retorno_total = equity[-1]
        max_dd = calcular_max_drawdown(equity)
        max_profit = equity.max()

        std_r = retornos.std(ddof=1) if n_ops > 1 else 0.0
        sharpe = (expectancy / std_r) * np.sqrt(252) if std_r > 0 else 0.0

        dd_ratio = max_dd / max_profit if max_profit > 0 else 1.0

        razones_rechazo = []
        if expectancy <= 0.02:
            razones_rechazo.append(f"Esperanza de {expectancy:+.2f}R (Insuficiente)")
        if ops_anuales < 12.0:
            razones_rechazo.append(f"Frecuencia de {ops_anuales:.1f} ops/ano (Volumen insuficiente)")
        if dd_ratio > 3.0: 
            razones_rechazo.append(f"Max DD del {dd_ratio:.1%} (Curva Inestable/Joroba)")
        if retorno_total <= 0:
            razones_rechazo.append("Retorno negativo")

        es_valido = len(razones_rechazo) == 0
        razon_str = " | ".join(razones_rechazo) if not es_valido else ""

        return {
            "Target_RR": 0.0, # Target RR dinámico (ya no se usa fijo)
            "Umbral": umbral,
            "Precision": prec,
            "Ops_Anio": ops_anuales,
            "Esperanza": expectancy,
            "Annual_R": annual_r,
            "Sharpe": sharpe,
            "Max_DD": max_dd,
            "Es_Valido": es_valido,
            "Razon_Rechazo": razon_str
        }

    resultados_raw = list(map(evaluar_umbral, umbrales))
    resultados_globales.extend([r for r in resultados_raw if r is not None])

    # Devolver dict_probs envuelto para no romper firma (usa 0.0 como key fake para target_rr)
    dict_probs = {0.0: probs}
    return dict_probs, resultados_globales


def entrenar_modelo_final(df: pd.DataFrame, features: list, activo: str, umbral: float):
    """
    Entrena el modelo final en el 100% de los datos prediciendo salida por inercia (+0.5R).
    """
    X = df[features]
    # PROTOCOLO V12: Net Profit Meta-Labeling
    synthetic_friction_pips = 2.5
    y = (df["Profit_Pips"] - synthetic_friction_pips > 0).astype(int)

    scaler = RobustScaler()
    X_sc = scaler.fit_transform(X)

    # Sample Weighting: proporcional a magnitud de Realized_RR
    rr_all = df["Realized_RR"].values
    weights = np.clip(np.abs(rr_all), 0.1, None)
    weights = weights / weights.mean()

    modelo = XGBClassifier(
        max_depth=3, learning_rate=0.02, n_estimators=300,
        subsample=0.8, colsample_bytree=0.8,
        reg_alpha=2.0, reg_lambda=5.0,
        eval_metric="logloss", tree_method="hist",
        random_state=42, n_jobs=-1, verbosity=0
    )
    modelo.fit(X_sc, y, sample_weight=weights)

    artefacto = {
        "model": modelo,
        "scaler": scaler,
        "features_activas": features,
        "threshold": umbral,
        "target_rr": 0.0 # Dinámico
    }

    out_path = os.path.join(OUT_DIR, f"modelo_francotirador_{activo.lower()}.pkl")
    joblib.dump(artefacto, out_path)
    print(f"[EXITO] Modelo serializado en: {out_path}")


# =============================================================================
# EJECUCION PRINCIPAL
# =============================================================================
def ejecutar_pipeline():
    print("=" * 70)
    print(f"  HMA META-LABELING — PIPELINE OPTIMIZACION (GRID RR): {ACTIVO.upper()}")
    print(f"  Folds TSS: {N_SPLITS} | Perfil: {PERFIL_SELECCIONADO}")
    print("=" * 70 + "\n")

    df, features = cargar_dataset(ACTIVO)

    if df is None or len(df) < 100:
        print(f"   [SKIP] Datos insuficientes para {ACTIVO.upper()}\n")
        return

    print(f"  Features detectadas: {len(features)} -> {features}\n")

    anos_datos = (df.index.max() - df.index.min()).days / 365.25
    dict_probs, resultados = entrenar_evaluar_oos(df, features, anos_datos)

    validos_list = [r for r in resultados if r["Es_Valido"]]
    
    if not resultados:
        print("\n[ADVERTENCIA] El modelo no encontro ningun umbral con mas de 10 operaciones. Abortando optimizacion.")
        return

    if not validos_list:
        mejor_bruto = max(resultados, key=lambda x: x["Annual_R"])
        print("=" * 115)
        print(f"  [ALERTA] NO SE ENCONTRARON PERFILES VALIDOS QUE CUMPLAN TODOS LOS FILTROS PARA {ACTIVO.upper()}")
        print("=" * 115)
        print(f"  [FALLBACK] Seleccionando mejor intento bruto: TP {mejor_bruto['Target_RR']}R | Umbral {mejor_bruto['Umbral']:.2f} | R_Anual: {mejor_bruto['Annual_R']:+.2f}R | Sharpe: {mejor_bruto['Sharpe']:.2f}")
        umbral_optimo = mejor_bruto["Umbral"]
        target_rr_optimo = mejor_bruto["Target_RR"]
    else:
        perfil_a = max(validos_list, key=lambda x: x["Sharpe"])
        perfil_b = max(validos_list, key=lambda x: x["Annual_R"])
        perfil_c = max(validos_list, key=lambda x: x["Sharpe"] * x["Annual_R"])

        perfiles = {
            "A": {"nombre": "Francotirador (Max Sharpe)", "data": perfil_a},
            "B": {"nombre": "Ametralladora (Max R_Anual)",  "data": perfil_b},
            "C": {"nombre": "Equilibrio Hibrido",           "data": perfil_c},
        }

        print("\n" + "=" * 125)
        print(f"  MENU DE ESTRATEGIAS VALIDAS: {ACTIVO.upper()}")
        print("=" * 125)
        print(f"  {'Perfil':<30} | {'TP (R)':<6} | {'Umbral':<8} | {'Precision':<10} | {'Ops/Anio':<8} | {'Esp.(R)':<8} | {'R_Anual':<8} | {'Sharpe':<8} | {'Max DD':<8}")
        print("-" * 125)

        for key, p in perfiles.items():
            res = p["data"]
            prec_str = f"{res['Precision']:.2%}"
            marker = " << SELECCIONADO" if key == PERFIL_SELECCIONADO else ""
            print(f"  [{key}] {p['nombre']:<26} | {res['Target_RR']:<6.2f} | {res['Umbral']:<8.2f} | {prec_str:<10} | {res['Ops_Anio']:<8.1f} | {res['Esperanza']:<8.2f} | {res['Annual_R']:<8.2f} | {res['Sharpe']:<8.2f} | {res['Max_DD']:<8.2f}R{marker}")

        print("-" * 125 + "\n")

        # Seleccion no-interactiva basada en argumento CLI
        seleccionado = perfiles.get(PERFIL_SELECCIONADO, perfiles["C"])["data"]
        umbral_optimo = seleccionado["Umbral"]
        target_rr_optimo = seleccionado["Target_RR"]
        print(f"[INFO] Perfil '{PERFIL_SELECCIONADO}' auto-seleccionado: TP {target_rr_optimo}R | Umbral {umbral_optimo:.2f}\n")

    # Guardar dataset con señales para analisis de correlacion
    df_senales = df.copy()
    # PROTOCOLO V12: Net Profit Meta-Labeling
    synthetic_friction_pips = 2.5
    df_senales["y_real"] = (df_senales["Profit_Pips"] - synthetic_friction_pips > 0).astype(int)
    df_senales["prob_ia"] = dict_probs[0.0]
    df_senales["Signal_IA"] = (df_senales["prob_ia"] >= umbral_optimo).astype(int)
    sig_path = os.path.join(OUT_DIR, f"senales_{ACTIVO.lower()}.csv")
    df_senales[["y_real", "prob_ia", "Signal_IA"]].to_csv(sig_path)

    # Guardar modelo final de produccion
    entrenar_modelo_final(df, features, ACTIVO, umbral_optimo)

    # Exportar JSON (Actualizando el existente si lo hay)
    config_path = os.path.join(OUT_DIR, "config_portfolio.json")
    config_dict = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_dict = json.load(f)

    config_dict[ACTIVO.lower()] = {
        "umbral": round(umbral_optimo, 2),
        "tp": "DYNAMIC_HMA"
    }
    with open(config_path, "w") as f:
        json.dump(config_dict, f, indent=4)
    print(f"[EXITO] Configuracion de produccion exportada a: {config_path}")


def ejecutar_scan_global():
    print("=" * 120)
    print(f"  HMA META-LABELING — ESCANER DE DESCUBRIMIENTO DE ALPHA GLOBAL")
    print("=" * 120 + "\n")

    archivos = glob.glob(os.path.join(DATA_DIR, "Struct_Dataset_*.csv"))
    if not archivos:
        print("  [WARN] No se encontraron archivos en data/")
        return

    def procesar_activo(f):
        activo = os.path.basename(f).replace("Struct_Dataset_", "").replace(".csv", "").lower()
        df, features = cargar_dataset(activo)
        if df is None or len(df) < 100:
            return {"Activo": activo.upper(), "Status": "[NO VALIDO - Datos insuficientes]"}

        anos_datos = (df.index.max() - df.index.min()).days / 365.25
        dict_probs, resultados = entrenar_evaluar_oos(df, features, anos_datos)

        validos_list = [r for r in resultados if r["Es_Valido"]]
        if not validos_list:
            mejor_bruto = max(resultados, key=lambda x: x["Annual_R"])
            return {
                "Activo": activo.upper(),
                "Status": f"[NO VALIDO - {mejor_bruto['Razon_Rechazo']}]"
            }

        perfil_hibrido = max(validos_list, key=lambda x: x["Sharpe"] * x["Annual_R"])
        return {
            "Activo": activo.upper(),
            "Status": "[VALIDO - Alpha Encontrado]",
            "Target_RR": perfil_hibrido["Target_RR"],
            "Umbral": perfil_hibrido["Umbral"],
            "Precision": perfil_hibrido["Precision"],
            "Ops": perfil_hibrido["Ops_Anio"],
            "Sharpe": perfil_hibrido["Sharpe"],
            "R_Anual": perfil_hibrido["Annual_R"]
        }

    resultados_scan = list(map(procesar_activo, archivos))

    print("=" * 130)
    print("  MATRIZ GLOBAL DE RESULTADOS OOS (CON GRID RR)")
    print("=" * 130)
    print(f"  {'Activo':<10} | {'Estado / TP Recomendado / Umbral':<50} | {'Precision':<10} | {'Ops/Anio':<8} | {'Sharpe':<8} | {'R_Anual':<8}")
    print("-" * 130)

    def imprimir_resultado(r):
        if "NO VALIDO" in r["Status"]:
            print(f"  {r['Activo']:<10} | {r['Status']:<50} | {'-':<10} | {'-':<8} | {'-':<8} | {'-':<8}")
        else:
            prec_str = f"{r['Precision']:.2%}"
            label = r["Status"] + f" (TP={r['Target_RR']}R | U={r['Umbral']})"
            print(f"  {r['Activo']:<10} | {label:<50} | {prec_str:<10} | {r['Ops']:<8.1f} | {r['Sharpe']:<8.2f} | {r['R_Anual']:<8.2f}R")

    list(map(imprimir_resultado, resultados_scan))
    print("=" * 120 + "\n")


if __name__ == "__main__":
    if MODO_SCAN:
        ejecutar_scan_global()
    else:
        ejecutar_pipeline()

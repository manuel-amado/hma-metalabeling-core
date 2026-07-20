# =============================================================================
# backtest_walk_forward_montecarlo.py — HMA Meta-Labeling System
# Fase 5: Validacion de Rentabilidad Real + Analisis de Estres Monte Carlo
# =============================================================================
# REFACTORING v2: Extraccion Dinamica de Features via LEAKAGE_COLS
#   - Elimina lista estatica FEATURES_ACTIVAS (9 features limitadas)
#   - Detecta las features de entrada dinamicamente por activo
#   - Soporta AUDCAD (17 features) y GBPUSD/USDJPY (20 features)
#   - dropna() matricial garantiza integridad indisoluble de indices
# =============================================================================

import os
import warnings
import numpy as np
import pandas as pd
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR       = os.path.join(BASE_DIR, "data")
OUT_DIR        = os.path.join(BASE_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

ACTIVO = sys.argv[1].lower() if len(sys.argv) > 1 else None

# ── Parametros del Experimento ────────────────────────────────────────────────
LOSS_PENALTY     = -1.0   # Perdida base por trade perdedor (en R)
N_MONTE_CARLO    = 1000   # Numero de caminos de bootstrap
N_SPLITS         = 5      # Folds TimeSeriesSplit

# ── Columnas post-trade (Data Leakage) que NUNCA son features de entrada ──────
# Extraccion dinamica: features = todas las columnas del CSV - LEAKAGE_COLS
LEAKAGE_COLS = [
    # -- Columnas post-trade directas (NUNCA features de entrada) ---------------
    "Ticket", "Time", "Signal_Type", "Entry_Price", "MFE_Pct", "MAE_Pct",
    "Max_RR_Achieved", "Realized_RR", "Close_Reason", "Profit_Pips", "Label",
    "Exact_Return_Pct", "Return_Pct", "Target", "y_real", "prob_ia", "retorno_r",
    # -- PURGA FORENSE DEFINITIVA (Zero-Trust) -- auditoria_antigravity v1 ------
    # Confirmado: ablacion PF 6.02 -> 0.96 al eliminar. Son post-trade o proxy.
    "Bars_In_Trade",   # POST-TRADE CRITICO: duracion del trade (corr=+0.584 con target)
    "Balance_Momento", # CONTAMINADA: equity actual codifica historial de P&L
    "Lots_Utilizados", # CONTAMINADA: lote calculado sobre equity actual
    # -- REHABILITADAS como pre-trade legitimas ---------------------------------
    # "Signal"       => PRE-TRADE: direccion BUY/SELL en apertura (ACTIVA)
    # "Pullback_Dur" => PRE-TRADE: duracion de estructura previa  (ACTIVA)
]



# =============================================================================
# 1. CARGA Y RE-LABELING MFE
# =============================================================================
def cargar_y_relabelar(activo: str) -> tuple:
    """
    Carga el CSV validando estructura y realiza el re-labeling dinamico
    (Realized_RR >= 0.5R) para la salida por HMA.
    """
    filename = f"Struct_Dataset_{activo.upper()}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] No encontrado: {filepath}")

    # Igualar logica de carga del pipeline multi-activo
    df = pd.read_csv(filepath, sep="\t", header=0, low_memory=False)
    if df.shape[1] == 1:
        df = pd.read_csv(filepath, sep=",", header=0, low_memory=False)

    df.columns = df.columns.str.strip()
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        df.set_index("Time", inplace=True)

    # Soporte bidireccional y robusto para datasets legacy / nuevos
    if "Max_RR_Achieved" in df.columns and "Realized_RR" not in df.columns:
        print(f"[WARN] {activo.upper()}: Dataset legacy detectado. Mapeando 'Max_RR_Achieved' a 'Realized_RR'.")
        df["Realized_RR"] = df["Max_RR_Achieved"]
    elif "Realized_RR" in df.columns and "Max_RR_Achieved" not in df.columns:
        df["Max_RR_Achieved"] = df["Realized_RR"]

    if "Realized_RR" not in df.columns:
        raise KeyError("[ERROR] 'Realized_RR' no encontrada. Requiere EA v2.1.")

    # Re-Labeling sintetico MFE (Inercia HMA)
    target_threshold_rr = 0.5
    df["y_real"] = (df["Realized_RR"] >= target_threshold_rr).astype(int)

    # Deteccion dinamica de features: todas las columnas - LEAKAGE_COLS
    features = [c for c in df.columns if c not in LEAKAGE_COLS]

    if not features:
        raise ValueError(f"[ERROR] No se detectaron features validas para {activo.upper()}")

    # Limpieza matricial ANTES de separar Features y Target
    cols_a_limpiar = features + ["y_real", "Realized_RR"]
    cols_existentes = [c for c in cols_a_limpiar if c in df.columns]
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=cols_existentes)

    tasa_base = df["y_real"].mean()
    print(f"  Senales cargadas: {len(df):,}")
    print(f"  Features detectadas: {len(features)} -> {features}")
    print(f"  Tasa Base (+0.5R Dinamico): {tasa_base:.2%} ({df['y_real'].sum():,} ganadoras)\n")

    return df, features


# =============================================================================
# 2. EXTRACCION DE PROBABILIDADES OOS (TSS manual)
# =============================================================================
def generar_probs_oos(df: pd.DataFrame, features: list) -> pd.DataFrame:
    """
    Genera probabilidades predict_proba estrictamente OOS.
    Acepta la lista dinamica de features para ser agnostico al activo.
    Preserva el indice cronologico del DataFrame para mantener
    la correspondencia con la curva de equidad real.
    """
    X = df[features]
    y = df["y_real"]

    tss   = TimeSeriesSplit(n_splits=N_SPLITS)
    probs = np.full(len(X), np.nan)

    for fold_idx, (train_idx, val_idx) in enumerate(tss.split(X), start=1):
        X_train_raw = X.iloc[train_idx]
        X_val_raw   = X.iloc[val_idx]
        y_train     = y.iloc[train_idx]

        scaler     = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc   = scaler.transform(X_val_raw)

        modelo = XGBClassifier(
            max_depth=3, learning_rate=0.02, n_estimators=300,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=2.0, reg_lambda=5.0,
            eval_metric="logloss", tree_method="hist",
            early_stopping_rounds=30,
            random_state=42, n_jobs=-1, verbosity=0,
        )

        # Sample Weighting: proporcional a magnitud de Realized_RR
        rr_train = df.iloc[train_idx]["Realized_RR"].values
        weights = np.clip(np.abs(rr_train), 0.1, None)
        weights = weights / weights.mean()

        modelo.fit(X_train_sc, y_train,
                   sample_weight=weights,
                   eval_set=[(X_val_sc, y.iloc[val_idx])],
                   verbose=False)
        probs[val_idx] = modelo.predict_proba(X_val_sc)[:, 1]
        print(f"  [Fold {fold_idx}/{N_SPLITS}] Train: {len(train_idx):,} | Val: {len(val_idx):,} OK")

    # Alinear con el DataFrame preservando el indice temporal
    df = df.copy()
    df["prob_ia"] = probs
    # Eliminar filas del primer bloque de entrenamiento puro (sin proba OOS)
    df = df.dropna(subset=["prob_ia"])
    print(f"\n  Total senales evaluadas OOS: {len(df):,}\n")
    return df


# =============================================================================
# 3. FILTRO FRANCOTIRADOR Y RETORNOS
# =============================================================================
def aplicar_filtro_y_calcular_retornos(df: pd.DataFrame, umbral: float) -> pd.DataFrame:
    """
    Filtra por umbral de confianza y asigna retorno en unidades R.
    Usa el Realized_RR dinámico, penalizando por slippage si se trata de un SL/salida negativa.
    """
    aprobados = df[df["prob_ia"] >= umbral].copy()

    # Friccion dinamica por spread
    if "Spread_Pips" in aprobados.columns and "SL_Pips_Reales" in aprobados.columns:
        friccion = aprobados["Spread_Pips"] / aprobados["SL_Pips_Reales"]
        friccion_capada = np.clip(friccion, 0.0, 0.5)
        penalty = -1.0 - friccion_capada.values
    else:
        penalty = np.full(len(aprobados), LOSS_PENALTY)

    # El retorno real es el Realized_RR si es positivo (salida HMA en beneficio).
    # Si es negativo, asumimos lo peor entre Realized_RR y un SL completo con penalty.
    rr_realizado = aprobados["Realized_RR"].values
    retornos = np.where(
        rr_realizado > 0,
        rr_realizado,
        np.minimum(rr_realizado, penalty)
    )
    aprobados["retorno_r"] = retornos
    return aprobados


# =============================================================================
# 4. METRICAS DE RENDIMIENTO
# =============================================================================
def calcular_max_drawdown(equity_curve: np.ndarray) -> float:
    """
    Calcula el Drawdown Maximo como la mayor caida desde un pico previo.
    Devuelve un valor positivo expresado en unidades R.
    """
    peak = np.maximum.accumulate(equity_curve)
    dd   = equity_curve - peak
    return float(-dd.min()) if len(dd) > 0 else 0.0


def imprimir_metricas(aprobados: pd.DataFrame, equity: np.ndarray, umbral: float, n_features: int):
    retornos  = aprobados["retorno_r"].values
    n_trades  = len(retornos)
    n_win     = (retornos > 0).sum()
    n_loss    = (retornos < 0).sum()
    win_rate  = n_win / n_trades if n_trades > 0 else 0.0

    retorno_total   = retornos.sum()
    ganancias_total = retornos[retornos > 0].sum()
    perdidas_total  = abs(retornos[retornos < 0].sum())
    profit_factor   = ganancias_total / perdidas_total if perdidas_total > 0 else float("inf")

    media_r  = retornos.mean()
    std_r    = retornos.std(ddof=1)
    sharpe   = (media_r / std_r) * np.sqrt(252) if std_r > 0 else 0.0

    max_dd_hist = calcular_max_drawdown(equity)

    print("=" * 65)
    print("  METRICAS DE RENDIMIENTO — SISTEMA DINAMICO v2")
    print(f"  Config: Umbral={umbral:.2f} | Features Dinamicas={n_features}")
    print("=" * 65)
    print(f"  Total Trades Aprobados :  {n_trades:,}")
    print(f"  Ganadores              :  {n_win:,}")
    print(f"  Perdedores             :  {n_loss:,}")
    print(f"  Win Rate               :  {win_rate:.2%}")
    print(f"  Retorno Total (R)      :  {retorno_total:+.2f}R")
    print(f"  Profit Factor          :  {profit_factor:.2f}")
    print(f"  Sharpe Ratio (R)       :  {sharpe:.2f}")
    print(f"  Max Drawdown Historico :  {max_dd_hist:.2f}R")
    print("=" * 65 + "\n")


# =============================================================================
# 5. SIMULACION DE MONTE CARLO (Bootstrap)
# =============================================================================
def simular_monte_carlo(retornos: np.ndarray, n_paths: int = N_MONTE_CARLO) -> tuple:
    """
    Bootstrap con reemplazo: genera N_MONTE_CARLO secuencias aleatorias
    de los mismos trades para estimar la distribucion de resultados posibles.

    INTERPRETACION FINANCIERA:
      Si todos los caminos de MC terminan en positivo, el sistema es robusto
      independientemente del orden en que ocurran los trades (el azar del
      orden no destruye la edge estadistica).
      Si muchos caminos terminan en negativo, el sistema depende demasiado
      de la secuencia historica especifica (overfitting temporal).
    """
    n_trades = len(retornos)
    rng      = np.random.default_rng(seed=42)

    # Generacion vectorizada de todos los caminos con una sola llamada numpy
    muestras = rng.choice(retornos, size=(n_paths, n_trades), replace=True)
    # Curvas de equidad: prefijo 0, luego cumsum vectorizado
    ceros    = np.zeros((n_paths, 1))
    paths    = np.cumsum(np.hstack([ceros, muestras]), axis=1)

    # Calculo vectorizado de Max Drawdown por camino
    peaks   = np.maximum.accumulate(paths, axis=1)
    dds     = paths - peaks
    max_dds = -dds.min(axis=1)

    print(f"  MC Drawdown Promedio ({n_paths:,} caminos) : {max_dds.mean():.2f}R")
    print(f"  MC Drawdown Percentil 95              : {np.percentile(max_dds, 95):.2f}R")
    print(f"  MC % caminos con retorno positivo     : {(paths[:, -1] > 0).mean():.2%}\n")

    return paths, max_dds


# =============================================================================
# 6. GRAFICOS PROFESIONALES (2 subplots)
# =============================================================================
def generar_graficos(aprobados: pd.DataFrame, equity: np.ndarray,
                     mc_paths: np.ndarray, activo: str, target_rr: float,
                     umbral: float, n_features: int):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.patch.set_facecolor("#0d1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#c9d1d9")
        ax.yaxis.label.set_color("#c9d1d9")
        ax.xaxis.label.set_color("#c9d1d9")
        ax.title.set_color("#e6edf3")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")

    # ── Subplot 1: Curva de Equidad Real (Walk-Forward) ──────────────────────
    ax1.set_title(
        f"Curva de Equidad Real (Walk-Forward OOS) | {activo.upper()} | "
        f"TP={target_rr}R | Umbral={umbral:.2f} | {n_features} Features",
        fontsize=11, pad=10
    )

    n = len(equity)
    ax1.plot(range(n), equity, color="#2f81f7", linewidth=1.5, zorder=3)
    ax1.fill_between(range(n), equity, 0,
                     where=(equity >= 0), color="#238636", alpha=0.15)
    ax1.fill_between(range(n), equity, 0,
                     where=(equity < 0), color="#da3633", alpha=0.15)
    ax1.axhline(0, color="#8b949e", linewidth=0.8, linestyle="--")

    retorno_final = equity[-1]
    color_final = "#3fb950" if retorno_final >= 0 else "#f85149"
    ax1.annotate(f"  Final: {retorno_final:+.2f}R",
                 xy=(n - 1, retorno_final),
                 fontsize=10, color=color_final, fontweight="bold")
    ax1.set_ylabel("Retorno Acumulado (R)", fontsize=10)
    ax1.set_xlabel("Numero de Trade", fontsize=10)
    ax1.grid(True, alpha=0.1, color="#30363d")

    # ── Subplot 2: Monte Carlo ────────────────────────────────────────────────
    ax2.set_title(f"Analisis de Estres Monte Carlo ({N_MONTE_CARLO:,} caminos bootstrap)",
                  fontsize=12, pad=10)

    # Dibujar un subconjunto aleatorio de caminos para no saturar el grafico
    rng_plot = np.random.default_rng(seed=99)
    idx_sample = rng_plot.choice(len(mc_paths), size=min(500, len(mc_paths)), replace=False)
    for path in mc_paths[idx_sample]:
        ax2.plot(path, color="#8b949e", alpha=0.03, linewidth=0.5)

    # Mediana resaltada
    mediana = np.median(mc_paths, axis=0)
    ax2.plot(mediana, color="#f85149", linewidth=2, label="Mediana MC", zorder=5)

    # Banda IQR P25-P75
    p25 = np.percentile(mc_paths, 25, axis=0)
    p75 = np.percentile(mc_paths, 75, axis=0)
    ax2.fill_between(range(len(mediana)), p25, p75, color="#f85149", alpha=0.1,
                     label="IQR (P25-P75)")

    # Percentil 5 (Worst Case)
    p05 = np.percentile(mc_paths, 5, axis=0)
    ax2.plot(p05, color="#da3633", linewidth=1, linestyle=":", label="P5 (Worst Case)", zorder=4)

    ax2.axhline(0, color="#8b949e", linewidth=0.8, linestyle="--")
    ax2.set_ylabel("Retorno Acumulado (R)", fontsize=10)
    ax2.set_xlabel("Numero de Trade", fontsize=10)
    ax2.legend(loc="upper left", facecolor="#161b22", edgecolor="#30363d",
               labelcolor="#c9d1d9", fontsize=9)
    ax2.grid(True, alpha=0.1, color="#30363d")

    plt.tight_layout(pad=2.0)
    plot_path = os.path.join(OUT_DIR, f"backtest_validation_{activo.lower()}.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Grafico guardado en: {plot_path}\n")


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================
def ejecutar():
    if not ACTIVO:
        print("[ERROR] Debes proporcionar un activo (ej. python backtest...py gbpusd)")
        return

    config_path = os.path.join(OUT_DIR, "config_portfolio.json")
    if not os.path.exists(config_path):
        print(f"[ERROR] No existe {config_path}. Ejecuta pipeline_multi_activo.py primero.")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    if ACTIVO not in config:
        print(f"[ERROR] El activo {ACTIVO.upper()} no esta en config_portfolio.json.")
        return

    params    = config[ACTIVO]
    umbral    = params["umbral"]
    target_rr_label = params.get("tp", "DYNAMIC")

    print("=" * 65)
    print("  HMA META-LABELING — BACKTEST WALK-FORWARD + MONTECARLO v2")
    print(f"  Config: {ACTIVO.upper()} | EXIT={target_rr_label} | Umbral={umbral}")
    print("=" * 65 + "\n")

    print("[1/6] Cargando y re-labeling dataset crudo...")
    try:
        df, features = cargar_y_relabelar(ACTIVO)
    except Exception as e:
        print(f"  [ERROR] {e}\n")
        return

    print("[2/6] Generando probabilidades OOS (TSS 5 folds)...")
    df_oos = generar_probs_oos(df, features)

    print("[3/6] Aplicando filtro Francotirador y calculando retornos...")
    aprobados = aplicar_filtro_y_calcular_retornos(df_oos, umbral)
    print(f"  Trades aprobados por el filtro IA: {len(aprobados):,} "
          f"de {len(df_oos):,} OOS ({len(aprobados)/len(df_oos):.1%})\n")

    if len(aprobados) < 10:
        print("[WARN] Menos de 10 trades aprobados. Resultados no estadisticamente validos.")
        return

    retornos = aprobados["retorno_r"].values
    equity   = np.cumsum(np.concatenate([[0], retornos]))

    print("[4/6] Calculando metricas de rendimiento...")
    imprimir_metricas(aprobados, equity, umbral, len(features))

    print("[5/6] Simulando Monte Carlo (1,000 caminos bootstrap — vectorizado)...")
    mc_paths, mc_dds = simular_monte_carlo(retornos)

    print("[6/6] Generando graficos de validacion...")
    generar_graficos(aprobados, equity, mc_paths, ACTIVO, target_rr_label, umbral, len(features))

    print(f"[OK] Ciclo de backtesting para {ACTIVO.upper()} completado.\n")


if __name__ == "__main__":
    ejecutar()

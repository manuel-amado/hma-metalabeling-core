# =============================================================================
# auditoria_antigravity.py — HMA Meta-Labeling System
# AUDITOR CUANTITATIVO FORENSE — v1.0
# =============================================================================
# MISION: Destruir el modelo actual y encontrar la fuga matematica.
# Implementa 4 pruebas de estres forense sobre el dataset GBPUSD.
#
# RESTRICCIONES ABSOLUTAS (Programacion Funcional Pura):
#   - PROHIBIDO: continue, break, pass, while True
#   - REQUERIDO:  vectorizacion numpy, map/filter/list comprehensions
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# =============================================================================
# CONFIGURACION
# =============================================================================
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUT_DIR    = os.path.join(BASE_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

ACTIVO     = sys.argv[1].lower() if len(sys.argv) > 1 else "gbpusd"
TARGET_RR  = 1.5
N_SPLITS   = 5
RANDOM_SEED = 42

# Columnas que DEFINITIVAMENTE son post-trade / leakage obvio
LEAKAGE_COLS = [
    "Ticket", "Time", "Signal_Type", "Entry_Price", "MFE_Pct", "MAE_Pct",
    "Max_RR_Achieved", "Close_Reason", "Profit_Pips", "Label",
    "Exact_Return_Pct", "Return_Pct", "Target", "y_real", "prob_ia", "retorno_r"
]

# Columnas SOSPECHOSAS: metricas que podrian contener info post-trade encubierta
# Seran marcadas con [SOSPECHOSA] en el Feature Dump
COLS_SOSPECHOSAS = {
    "Bars_In_Trade":    "POST-TRADE: duracion del trade, solo conocida al cierre",
    "Pullback_Dur":     "SOSPECHOSA: duracion del pullback previo, puede ser calculada a posteriori",
    "Balance_Momento":  "SOSPECHOSA: refleja el equity actual — puede codificar el historial de P&L",
    "Lots_Utilizados":  "SOSPECHOSA: lote calculado sobre balance actual — correlacionado con equity",
    "MAE_Pct":          "POST-TRADE CRITICO: Max Adverse Excursion, solo conocida al cierre",
    "MFE_Pct":          "POST-TRADE CRITICO: Max Favorable Excursion, solo conocida al cierre",
    "Signal":           "SOSPECHOSA: verificar si codifica la direccion de trade (BUY=1/SELL=0)",
}

SEPARADOR = "=" * 80


# =============================================================================
# UTILIDADES COMPARTIDAS
# =============================================================================
def cargar_dataset_forense(activo: str) -> tuple:
    """
    Carga el CSV y devuelve (df_completo, lista_features_actuales, lista_y).
    NO aplica ningun filtro de outliers para ver el dataset en bruto.
    """
    filename = f"Struct_Dataset_{activo.upper()}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] Archivo no encontrado: {filepath}")

    df = pd.read_csv(filepath, sep="\t", header=0, low_memory=False)
    if df.shape[1] == 1:
        df = pd.read_csv(filepath, sep=",", header=0, low_memory=False)

    df.columns = df.columns.str.strip()
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        df.set_index("Time", inplace=True)

    if "Max_RR_Achieved" not in df.columns:
        raise KeyError("'Max_RR_Achieved' no encontrada. Requiere EA v2.1.")

    # Re-labeling sintetico MFE (igual que el pipeline)
    df["y_real"] = (df["Max_RR_Achieved"] >= TARGET_RR).astype(int)

    # Lista de features dinamica (igual que el pipeline refactorizado)
    features = [c for c in df.columns if c not in LEAKAGE_COLS]

    # Limpieza matricial
    cols_limpiar = [c for c in features + ["y_real", "Max_RR_Achieved"] if c in df.columns]
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=cols_limpiar)
    if "SL_Dist_ATR" in df.columns:
        df = df[df["SL_Dist_ATR"] <= 10]
    if "Breakout_Force_ATR" in df.columns:
        df = df[df["Breakout_Force_ATR"] <= 8]

    return df, features


def entrenar_fold_unico(X_train_sc: np.ndarray, y_train: np.ndarray,
                        X_val_sc: np.ndarray) -> np.ndarray:
    """Entrena un XGBClassifier en un fold y devuelve probabilidades OOS."""
    modelo = XGBClassifier(
        max_depth=3, learning_rate=0.05, n_estimators=100,
        subsample=0.8, colsample_bytree=0.8,
        reg_alpha=1.0, reg_lambda=2.0,
        eval_metric="logloss", tree_method="hist",
        random_state=RANDOM_SEED, n_jobs=-1, verbosity=0,
    )
    modelo.fit(X_train_sc, y_train)
    return modelo.predict_proba(X_val_sc)[:, 1], modelo


def calcular_metricas_rapidas(y_real: np.ndarray, probs: np.ndarray,
                               umbral: float) -> dict:
    """Calcula Win Rate y Profit Factor de forma vectorizada."""
    aprobadas_mask = probs >= umbral
    n_aprobadas = aprobadas_mask.sum()

    if n_aprobadas == 0:
        return {"n_trades": 0, "win_rate": 0.0, "profit_factor": 0.0}

    y_aprobadas = y_real[aprobadas_mask]
    n_win   = (y_aprobadas == 1).sum()
    n_loss  = (y_aprobadas == 0).sum()
    win_rate = n_win / n_aprobadas

    retornos = np.where(y_aprobadas == 1, 1.5, -1.0)
    ganancias = retornos[retornos > 0].sum()
    perdidas  = abs(retornos[retornos < 0].sum())
    pf = ganancias / perdidas if perdidas > 0 else (ganancias if ganancias > 0 else 0.0)

    return {
        "n_trades":     int(n_aprobadas),
        "win_rate":     float(win_rate),
        "profit_factor": float(pf),
    }


# =============================================================================
# PRUEBA 1: FEATURE DUMP — AUDITORIA EXPLICITA DE COLUMNAS
# =============================================================================
def prueba_1_feature_dump(df: pd.DataFrame, features: list):
    """
    Imprime la lista EXACTA de columnas que entran en X.
    Marca cada feature con su categoria de riesgo de leakage.
    Calcula la correlacion de Pearson de cada feature con el target.
    """
    print(f"\n{SEPARADOR}")
    print("  PRUEBA 1: FEATURE DUMP — AUDITORIA EXPLICITA DE COLUMNAS")
    print(f"{SEPARADOR}")
    print(f"  Activo: {ACTIVO.upper()} | Total features en X: {len(features)}\n")

    y = df["y_real"].values

    def analizar_feature(col: str) -> dict:
        serie = df[col].values.astype(float)
        # Correlacion de Pearson con el target
        corr = float(np.corrcoef(serie, y)[0, 1]) if np.std(serie) > 0 else 0.0
        sospecha = COLS_SOSPECHOSAS.get(col, "OK")
        return {"col": col, "corr": corr, "sospecha": sospecha}

    resultados = list(map(analizar_feature, features))
    resultados_ordenados = sorted(resultados, key=lambda x: abs(x["corr"]), reverse=True)

    print(f"  {'#':<3} | {'Feature':<25} | {'Corr(X,y)':<12} | {'Estado'}")
    print(f"  {'-'*3}-+-{'-'*25}-+-{'-'*12}-+-{'-'*40}")

    def imprimir_feature(idx_res):
        i, res = idx_res
        estado = f"[!!] {res['sospecha']}" if res['sospecha'] != "OK" else "[ OK ]"
        alert  = "***" if abs(res['corr']) > 0.15 else ("  *" if abs(res['corr']) > 0.05 else "   ")
        print(f"  {i+1:<3} | {res['col']:<25} | {res['corr']:>+.6f} {alert} | {estado}")

    list(map(imprimir_feature, enumerate(resultados_ordenados)))

    # Veredicto de correlacion alta
    alta_corr = [r for r in resultados_ordenados if abs(r["corr"]) > 0.15]
    sospechosas_presentes = [r for r in resultados_ordenados if r["sospecha"] != "OK"]

    print(f"\n  [VEREDICTO FEATURE DUMP]")
    print(f"  Features con |corr| > 0.15: {len(alta_corr)}")
    print(f"  Features marcadas SOSPECHOSAS: {len(sospechosas_presentes)}")

    if sospechosas_presentes:
        print(f"\n  [ALERTA CRITICA] Las siguientes features SOSPECHOSAS estan en X:")
        list(map(lambda r: print(f"    - {r['col']}: {r['sospecha']}"), sospechosas_presentes))

    return resultados_ordenados


# =============================================================================
# PRUEBA 2: ANALISIS DE IMPORTANCIA DE FEATURES (Feature Importance + Grafico)
# =============================================================================
def prueba_2_feature_importance(df: pd.DataFrame, features: list):
    """
    Entrena un modelo en el ultimo fold de TimeSeriesSplit y exporta:
    - Top 10 features por importancia XGBoost (gain)
    - Grafico shap_audit.png con barras horizontales
    Detecta si alguna feature tiene dominancia > 40% (sospecha de leakage).
    """
    print(f"\n{SEPARADOR}")
    print("  PRUEBA 2: ANALISIS DE IMPORTANCIA (SHAP proxy via XGBoost gain)")
    print(f"{SEPARADOR}")

    X = df[features].values
    y = df["y_real"].values

    tss = TimeSeriesSplit(n_splits=N_SPLITS)
    splits = list(tss.split(X))
    # Usar solo el ultimo fold (mayor train set, mas representativo)
    train_idx, val_idx = splits[-1]

    scaler     = RobustScaler()
    X_train_sc = scaler.fit_transform(X[train_idx])
    X_val_sc   = scaler.transform(X[val_idx])

    _, modelo = entrenar_fold_unico(X_train_sc, y[train_idx], X_val_sc)

    importancias_raw = modelo.feature_importances_
    total = importancias_raw.sum() if importancias_raw.sum() > 0 else 1.0
    importancias_norm = importancias_raw / total

    feature_imp = sorted(
        zip(features, importancias_norm),
        key=lambda x: x[1],
        reverse=True
    )

    print(f"\n  TOP 10 FEATURES POR IMPORTANCIA (XGBoost gain, normalizado):\n")
    print(f"  {'#':<3} | {'Feature':<25} | {'Importancia':>12} | {'Barra'}")
    print(f"  {'-'*3}-+-{'-'*25}-+-{'-'*12}-+-{'-'*30}")

    def imprimir_importancia(idx_fi):
        i, (feat, imp) = idx_fi
        barra = "#" * int(imp * 50)
        alerta = " [!!!] DOMINANCIA ANORMAL" if imp > 0.40 else (
                 " [!!] SOSPECHOSA"          if imp > 0.25 else "")
        print(f"  {i+1:<3} | {feat:<25} | {imp:>11.2%} | {barra}{alerta}")

    list(map(imprimir_importancia, enumerate(feature_imp[:10])))

    # Veredicto
    imp_max_feat, imp_max_val = feature_imp[0]
    print(f"\n  [VEREDICTO IMPORTANCIA]")
    print(f"  Feature dominante: '{imp_max_feat}' con {imp_max_val:.2%} del peso total.")
    if imp_max_val > 0.40:
        print(f"  [ALERTA CRITICA] Dominancia > 40% => Sospecha grave de Data Leakage en '{imp_max_feat}'")
    elif imp_max_val > 0.25:
        print(f"  [ADVERTENCIA] Dominancia > 25% => Investigar '{imp_max_feat}' mas en detalle.")
    else:
        print(f"  [NORMAL] Distribucion de importancias equilibrada. Sin dominancia anormal.")

    # Generar grafico
    top_n = min(15, len(feature_imp))
    names  = [f[0] for f in feature_imp[:top_n]][::-1]
    values = [f[1] for f in feature_imp[:top_n]][::-1]
    colors = ["#f85149" if v > 0.25 else ("#f0883e" if v > 0.10 else "#3fb950") for v in values]

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#c9d1d9")
    ax.xaxis.label.set_color("#c9d1d9")
    ax.yaxis.label.set_color("#c9d1d9")
    ax.title.set_color("#e6edf3")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")

    bars = ax.barh(names, values, color=colors, edgecolor="#30363d", linewidth=0.5)

    # Etiquetas de valor
    def etiquetar_barra(bar):
        width = bar.get_width()
        ax.text(width + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{width:.2%}", va="center", ha="left",
                color="#c9d1d9", fontsize=9)

    list(map(etiquetar_barra, bars))

    ax.axvline(0.40, color="#f85149", linewidth=1.5, linestyle="--",
               label="Umbral Critico (40%)")
    ax.axvline(0.25, color="#f0883e", linewidth=1.0, linestyle=":",
               label="Umbral Advertencia (25%)")
    ax.set_xlabel("Importancia Relativa (XGBoost gain)", fontsize=10)
    ax.set_title(f"Auditoria Forense de Importancia de Features — {ACTIVO.upper()} (Fold {N_SPLITS}/{N_SPLITS})",
                 fontsize=12, pad=12)
    ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=9)
    ax.grid(True, axis="x", alpha=0.1, color="#30363d")

    plt.tight_layout(pad=1.5)
    plot_path = os.path.join(OUT_DIR, f"shap_audit_{ACTIVO.lower()}.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  Grafico guardado en: {plot_path}")

    return feature_imp


# =============================================================================
# PRUEBA 3: PERMUTATION TEST (PRUEBA DE CORDURA)
# =============================================================================
def prueba_3_permutation_test(df: pd.DataFrame, features: list):
    """
    PRUEBA DE CORDURA:
    Entrena XGBoost con etiquetas y_train ALEATORIAS (permutadas).
    Si el modelo sigue generando Profit Factor > 1.0 o Win Rate > 55%
    con datos aleatorios, el backtest esta ESTRUCTURALMENTE ROTO.

    Ejecuta N_SPLITS permutaciones independientes y reporta estadisticas.
    """
    print(f"\n{SEPARADOR}")
    print("  PRUEBA 3: PERMUTATION TEST — PRUEBA DE CORDURA ESTRUCTURAL")
    print(f"{SEPARADOR}")
    print("  Hipotesis nula: Un modelo entrenado con etiquetas ALEATORIAS")
    print("  NO puede generar Profit Factor > 1.0 en OOS.")
    print("  Si lo hace, el pipeline esta roto independientemente de las features.\n")

    X  = df[features].values
    y  = df["y_real"].values

    tss    = TimeSeriesSplit(n_splits=N_SPLITS)
    splits = list(tss.split(X))
    rng    = np.random.default_rng(seed=RANDOM_SEED)

    # Umbral fijo para la evaluacion (el optimo del scanner)
    UMBRAL_EVAL = 0.50

    def evaluar_fold_permutado(fold_data):
        fold_idx, (train_idx, val_idx) = fold_data
        X_train_raw, X_val_raw = X[train_idx], X[val_idx]
        y_train_real            = y[train_idx]
        y_val_real              = y[val_idx]

        # PERMUTACION: mezcla aleatoria del target de entrenamiento
        y_train_shuffled = rng.permutation(y_train_real)

        scaler     = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train_raw)
        X_val_sc   = scaler.transform(X_val_raw)

        probs_permutado, _ = entrenar_fold_unico(X_train_sc, y_train_shuffled, X_val_sc)

        # Metricas con labels REALES de validacion (para ver si hay edge residual)
        metricas = calcular_metricas_rapidas(y_val_real, probs_permutado, UMBRAL_EVAL)
        metricas["fold"] = fold_idx + 1
        return metricas

    resultados = list(map(evaluar_fold_permutado, enumerate(splits)))

    print(f"  Umbral de evaluacion: {UMBRAL_EVAL:.2f}")
    print(f"\n  {'Fold':<5} | {'N Trades':>8} | {'Win Rate':>10} | {'Profit Factor':>14}")
    print(f"  {'-'*5}-+-{'-'*8}-+-{'-'*10}-+-{'-'*14}")

    def imprimir_fold(res):
        flag = " [!!]" if res["profit_factor"] > 1.2 or res["win_rate"] > 0.58 else ""
        print(f"  {res['fold']:<5} | {res['n_trades']:>8,} | {res['win_rate']:>9.2%} | {res['profit_factor']:>13.2f}{flag}")

    list(map(imprimir_fold, resultados))

    # Estadisticas agregadas
    win_rates = np.array([r["win_rate"] for r in resultados])
    pfs       = np.array([r["profit_factor"] for r in resultados])

    print(f"\n  [RESUMEN PERMUTATION TEST]")
    print(f"  Win Rate promedio  (labels aleatorias): {win_rates.mean():.2%} (+/- {win_rates.std():.2%})")
    print(f"  Profit Factor medio (labels aleatorias): {pfs.mean():.2f}      (+/- {pfs.std():.2f})")

    UMBRAL_ROTURA = 1.20  # PF > 1.2 con labels aleatorias es evidencia de rotura
    folds_rotos = (pfs > UMBRAL_ROTURA).sum()

    print(f"\n  [VEREDICTO PERMUTATION TEST]")
    if folds_rotos >= 2:
        print(f"  [ALERTA CRITICA] {folds_rotos}/{N_SPLITS} folds con PF > {UMBRAL_ROTURA} con labels ALEATORIAS.")
        print(f"  => El backtest esta ESTRUCTURALMENTE ROTO. La edge NO viene del modelo.")
    elif pfs.mean() > 1.0:
        print(f"  [ADVERTENCIA] PF medio > 1.0 con labels aleatorias. Investigar estructura del pipeline.")
    else:
        print(f"  [NORMAL] PF medio ~ {pfs.mean():.2f} con labels aleatorias.")
        print(f"  => El pipeline es correcto. La edge SI proviene del modelo.")

    return resultados


# =============================================================================
# PRUEBA 4: DETECCION DE LOOK-AHEAD BIAS EN NORMALIZACION Y FEATURES
# =============================================================================
def prueba_4_lookahead_bias(df: pd.DataFrame, features: list):
    """
    VERIFICACION DE LOOK-AHEAD BIAS:
    1. Verifica que el Z_Score del CSV NO fue calculado sobre el dataset completo.
       (Si lo fue, el modelo ve el futuro en la normalizacion de entrada.)
    2. Compara el comportamiento del modelo con y sin RobustScaler para aislar
       si el scaler introduce sesgo de futuro.
    3. Verifica la distribucion temporal de cada feature sospechosa
       para detectar si cambia de comportamiento en los ultimos folds
       (indicio de that el calculo incluye datos futuros).
    """
    print(f"\n{SEPARADOR}")
    print("  PRUEBA 4: DETECCION DE LOOK-AHEAD BIAS EN NORMALIZACION Y FEATURES")
    print(f"{SEPARADOR}")

    n_total = len(df)
    tss     = TimeSeriesSplit(n_splits=N_SPLITS)
    splits  = list(tss.split(df))

    # 4A: Verificacion de Z_Score columnaro (calculado en bloque)
    print("\n  [4A] Verificacion de Z_Score columnar (datos de apertura):")
    if "Z_Score" in df.columns:
        z = df["Z_Score"].values
        # Si Z_Score fue calculado en bloque sobre todo el CSV, su media deberia
        # ser muy cercana a 0 y su std cercana a 1 (estandarizacion perfecta)
        z_mean = np.mean(z)
        z_std  = np.std(z)
        print(f"    Z_Score: media={z_mean:.4f}, std={z_std:.4f}")
        if abs(z_mean) < 0.05 and abs(z_std - 1.0) < 0.1:
            print("    [ALERTA] Z_Score parece calculado sobre el DATASET COMPLETO.")
            print("    => Si se calculo ANTES de separar los folds, hay Look-Ahead Bias.")
            print("    => El modelo ve la media/std de TRADES FUTUROS en cada Z_Score.")
        else:
            print("    [OK] Z_Score no parece estandarizado globalmente (media/std no en [0,1]).")
    else:
        print("    Z_Score no encontrado en el dataset.")

    # 4B: Verificacion de RobustScaler — comparar con/sin scaler en fold 5
    print("\n  [4B] Verificacion de RobustScaler (scaler fitteado en train, NO en todo el dataset):")

    X = df[features].values
    y = df["y_real"].values
    train_idx, val_idx = splits[-1]

    # CON scaler fitteado solo en train (CORRECTO)
    scaler_correcto = RobustScaler()
    X_tr_sc = scaler_correcto.fit_transform(X[train_idx])
    X_va_sc = scaler_correcto.transform(X[val_idx])
    probs_correcto, _ = entrenar_fold_unico(X_tr_sc, y[train_idx], X_va_sc)
    met_correcto = calcular_metricas_rapidas(y[val_idx], probs_correcto, 0.50)

    # CON scaler fitteado en TODO el dataset (INCORRECTO — Look-Ahead)
    scaler_leaky = RobustScaler()
    X_todo_sc    = scaler_leaky.fit_transform(X)
    probs_leaky, _ = entrenar_fold_unico(
        X_todo_sc[train_idx], y[train_idx], X_todo_sc[val_idx]
    )
    met_leaky = calcular_metricas_rapidas(y[val_idx], probs_leaky, 0.50)

    print(f"    {'Metodo':<40} | {'Win Rate':>10} | {'Profit Factor':>14}")
    print(f"    {'-'*40}-+-{'-'*10}-+-{'-'*14}")
    print(f"    {'Scaler CORRECTO (fit solo en train)':<40} | {met_correcto['win_rate']:>9.2%} | {met_correcto['profit_factor']:>13.2f}")
    print(f"    {'Scaler LEAKY (fit en TODO el dataset)':<40} | {met_leaky['win_rate']:>9.2%} | {met_leaky['profit_factor']:>13.2f}")

    delta_pf = met_leaky["profit_factor"] - met_correcto["profit_factor"]
    if abs(delta_pf) > 0.5:
        print(f"\n    [ALERTA] Delta PF = {delta_pf:+.2f}. El scaler global INFLA artificialmente el rendimiento.")
    else:
        print(f"\n    [OK] Delta PF = {delta_pf:+.2f}. El RobustScaler no introduce sesgo significativo.")

    # 4C: Deriva temporal de features sospechosas
    print("\n  [4C] Analisis de deriva temporal de features sospechosas:")
    cols_sospechosas_presentes = [c for c in COLS_SOSPECHOSAS if c in features]

    def analizar_deriva(col: str) -> dict:
        serie = df[col].values
        # Dividir en 5 bloques temporales iguales
        bloques = np.array_split(serie, N_SPLITS)
        medias  = np.array([b.mean() for b in bloques])
        std_between = np.std(medias)
        rango_relativo = (medias.max() - medias.min()) / (abs(medias.mean()) + 1e-9)
        return {
            "col": col,
            "medias_bloque": medias,
            "std_between": std_between,
            "rango_relativo": rango_relativo,
        }

    derivas = list(map(analizar_deriva, cols_sospechosas_presentes))

    def imprimir_deriva(d):
        medias_str = " | ".join([f"{m:+.2f}" for m in d["medias_bloque"]])
        alerta     = " [!!] NO ESTACIONARIA" if d["rango_relativo"] > 1.0 else " [OK]"
        print(f"    {d['col']:<25}: [{medias_str}] rango_rel={d['rango_relativo']:.2f}{alerta}")

    list(map(imprimir_deriva, derivas))

    print(f"\n  [VEREDICTO 4C]")
    no_estacionarias = [d for d in derivas if d["rango_relativo"] > 1.0]
    if no_estacionarias:
        print(f"  [ALERTA] {len(no_estacionarias)} features sospechosas son NO ESTACIONARIAS en el tiempo.")
        print(f"  => Si el modelo aprende la tendencia temporal de estas features,")
        print(f"     puede estar explotando patrones de drift y no edge real.")
    else:
        print(f"  [OK] Features sospechosas aproximadamente estacionarias. Sin deriva temporal evidente.")

    return derivas


# =============================================================================
# PRUEBA BONUS: TEST DE ABLACION — Rendimiento CON vs SIN features sospechosas
# =============================================================================
def prueba_bonus_ablacion(df: pd.DataFrame, features: list, feature_imp: list):
    """
    Compara el modelo COMPLETO (20 features) vs el modelo PODADO
    (sin Bars_In_Trade, Balance_Momento, Lots_Utilizados, Pullback_Dur).
    Si el podado rinde lo mismo, las features sospechosas son irrelevantes.
    Si el rendimiento cae dramaticamente, eran fundamentales y sospechosas.
    Si el rendimiento MEJORA sin ellas, eran ruido o leakage.
    """
    print(f"\n{SEPARADOR}")
    print("  PRUEBA BONUS: TEST DE ABLACION — CON vs SIN features sospechosas")
    print(f"{SEPARADOR}")

    UMBRAL = 0.50
    X_completo = df[features].values
    y          = df["y_real"].values

    features_podadas = [f for f in features if f not in COLS_SOSPECHOSAS]
    X_podado = df[features_podadas].values

    tss    = TimeSeriesSplit(n_splits=N_SPLITS)
    splits = list(tss.split(X_completo))

    def evaluar_configuracion(X_data: np.ndarray, nombre: str) -> dict:
        probs_oos = np.full(len(y), np.nan)

        def procesar_fold(fold_data):
            _, (train_idx, val_idx) = fold_data
            scaler     = RobustScaler()
            X_tr_sc    = scaler.fit_transform(X_data[train_idx])
            X_va_sc    = scaler.transform(X_data[val_idx])
            probs, _   = entrenar_fold_unico(X_tr_sc, y[train_idx], X_va_sc)
            probs_oos[val_idx] = probs

        list(map(procesar_fold, enumerate(splits)))

        validos = ~np.isnan(probs_oos)
        metricas = calcular_metricas_rapidas(y[validos], probs_oos[validos], UMBRAL)
        metricas["nombre"] = nombre
        metricas["n_features"] = X_data.shape[1]
        return metricas

    met_completo = evaluar_configuracion(X_completo, f"COMPLETO ({len(features)} features)")
    met_podado   = evaluar_configuracion(X_podado,   f"PODADO   ({len(features_podadas)} features, sin sospechosas)")

    print(f"\n  {'Configuracion':<45} | {'N Features':>10} | {'Win Rate':>10} | {'Profit Factor':>14}")
    print(f"  {'-'*45}-+-{'-'*10}-+-{'-'*10}-+-{'-'*14}")

    def imprimir_met(m):
        print(f"  {m['nombre']:<45} | {m['n_features']:>10} | {m['win_rate']:>9.2%} | {m['profit_factor']:>13.2f}")

    list(map(imprimir_met, [met_completo, met_podado]))

    delta_pf = met_podado["profit_factor"] - met_completo["profit_factor"]
    delta_wr = met_podado["win_rate"] - met_completo["win_rate"]

    print(f"\n  [Delta] PF: {delta_pf:+.2f} | Win Rate: {delta_wr:+.2%}")
    print(f"\n  [VEREDICTO ABLACION]")

    if met_podado["profit_factor"] > met_completo["profit_factor"] * 0.9:
        print(f"  [OK] El modelo PODADO rinde igual o mejor que el COMPLETO.")
        print(f"  => Las features sospechosas son PRESCINDIBLES. Se pueden eliminar de forma segura.")
    elif delta_pf < -0.5:
        print(f"  [ALERTA] El modelo PODADO rinde significativamente PEOR.")
        print(f"  => Las features sospechosas APORTAN informacion predictiva real o...")
        print(f"     ...estan introduciendo Data Leakage que infla artificialmente el rendimiento.")
    else:
        print(f"  [NEUTRAL] Diferencia marginal. Las features sospechosas aportan poco valor.")

    # Features podadas usadas (para reportar)
    print(f"\n  Features eliminadas en el test de ablacion:")
    cols_eliminadas = [f for f in features if f in COLS_SOSPECHOSAS]
    list(map(lambda c: print(f"    - {c}: {COLS_SOSPECHOSAS[c]}"), cols_eliminadas))

    return met_completo, met_podado


# =============================================================================
# ORQUESTADOR PRINCIPAL
# =============================================================================
def ejecutar_auditoria():
    print(f"\n{'#' * 80}")
    print(f"#  AUDITOR CUANTITATIVO FORENSE — HMA META-LABELING SYSTEM")
    print(f"#  Activo: {ACTIVO.upper()} | Target RR: {TARGET_RR}R | Folds: {N_SPLITS}")
    print(f"#  Fecha de auditoria: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#' * 80}\n")

    print("[*] Cargando dataset para auditoria forense...")
    df, features = cargar_dataset_forense(ACTIVO)

    print(f"[*] Dataset cargado: {len(df):,} filas | {len(df.columns)} columnas totales")
    print(f"[*] Features en X: {len(features)} | Target base rate: {df['y_real'].mean():.2%}")

    # Ejecutar las 4 pruebas en secuencia
    resultados_dump     = prueba_1_feature_dump(df, features)
    feature_imp         = prueba_2_feature_importance(df, features)
    resultados_perm     = prueba_3_permutation_test(df, features)
    derivas             = prueba_4_lookahead_bias(df, features)
    met_completo, met_podado = prueba_bonus_ablacion(df, features, feature_imp)

    # Dictamen Final
    print(f"\n{'#' * 80}")
    print(f"#  DICTAMEN FORENSE FINAL — {ACTIVO.upper()}")
    print(f"{'#' * 80}")

    imp_max_feat, imp_max_val = feature_imp[0]
    pfs_perm = np.array([r["profit_factor"] for r in resultados_perm])

    dictamen_items = [
        (imp_max_val > 0.40,
         f"[CULPABLE] '{imp_max_feat}' domina con {imp_max_val:.1%} del peso. Data Leakage probable."),
        ((pfs_perm > 1.2).sum() >= 2,
         f"[CULPABLE] Permutation Test fallo: {(pfs_perm > 1.2).sum()}/{N_SPLITS} folds positivos con labels aleatorias. Pipeline roto."),
        (met_podado["profit_factor"] < met_completo["profit_factor"] * 0.7,
         "[CULPABLE] Ablacion critica: el rendimiento cae >30% sin las features sospechosas."),
        (imp_max_val <= 0.40 and (pfs_perm > 1.2).sum() < 2 and
         met_podado["profit_factor"] >= met_completo["profit_factor"] * 0.7,
         "[ABSUELTO] Ninguna prueba detecta Data Leakage estructural. La edge puede ser real."),
    ]

    def imprimir_dictamen(item):
        condicion, mensaje = item
        if condicion:
            print(f"  {mensaje}")

    list(map(imprimir_dictamen, dictamen_items))
    print(f"\n  Shap audit guardado en: {os.path.join(OUT_DIR, f'shap_audit_{ACTIVO.lower()}.png')}")
    print(f"{'#' * 80}\n")


if __name__ == "__main__":
    ejecutar_auditoria()

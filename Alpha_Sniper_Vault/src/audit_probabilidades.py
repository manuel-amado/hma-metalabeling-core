"""
AUDITORIA EXHAUSTIVA DE PROBABILIDADES
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import pandas as pd
import numpy as np
import os
import joblib
import re

AUDIT_FILE = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\mql5_feature_audit.txt"
DATA_DIR   = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data"
MODELS_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\models"

# ── 1. Parse audit file ──────────────────────────────────────────────────────
rows = []
with open(AUDIT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";", 2)
        if len(parts) < 3:
            continue
        ts, sym, payload = parts
        try:
            d = json.loads(payload)
            d["_sym"] = sym.strip()
            d["_ts"]  = ts.strip()
            rows.append(d)
        except Exception:
            continue

live = pd.DataFrame(rows)
print(f"Total señales parseadas del audit file: {len(live)}")
print(f"Símbolos: {live['_sym'].value_counts().to_dict()}")
print()

# ── 2. Feature columns (excluding metadata) ──────────────────────────────────
FEAT_COLS = [c for c in live.columns if c not in ("_sym","_ts","activo")]

# ── 3. Per-symbol analysis ───────────────────────────────────────────────────
SYMBOLS = ["XAUUSD", "EURJPY", "EURUSD", "USDJPY", "XAGUSD", "GBPUSD"]

print("=" * 80)
print("SECCIÓN A: ESTADÍSTICAS POR SÍMBOLO (FEATURES ENVIADAS AL SERVIDOR)")
print("=" * 80)

live_stats = {}
for sym in SYMBOLS:
    sub = live[live["_sym"] == sym]
    if len(sub) == 0:
        print(f"\n{sym}: NO HAY SEÑALES en el archivo de auditoría")
        continue
    print(f"\n{'─'*50}")
    print(f"{sym} — {len(sub)} señales")
    print(f"  Periodo: {sub['_ts'].iloc[0]} → {sub['_ts'].iloc[-1]}")

    stats = sub[FEAT_COLS].describe().T[["mean","std","min","max"]]
    live_stats[sym] = stats

    # Show key features
    key = ["Z_Score","ATR_Norm","RSI","HMA_Slope_Pct","Breakout_Force_ATR",
           "SL_Dist_ATR","MTF_ATR_Ratio","Dist_Macro_EMA","Energy_Accumulation",
           "Spread_Impact_Ratio","Vol_Spread_Ratio"]
    avail = [c for c in key if c in stats.index]
    print(stats.loc[avail].to_string())

# ── 4. Compare vs training dataset distributions ─────────────────────────────
print()
print("=" * 80)
print("SECCIÓN B: DRIFT ANALYSIS — LIVE vs TRAINING")
print("=" * 80)

for sym in ["XAUUSD", "EURJPY", "USDJPY", "EURUSD", "XAGUSD"]:
    dpath = os.path.join(DATA_DIR, f"Struct_Dataset_{sym}.csv")
    if not os.path.exists(dpath):
        continue
    train = pd.read_csv(dpath)
    train.columns = [c.strip() for c in train.columns]

    sub_live = live[live["_sym"] == sym]
    if len(sub_live) == 0:
        print(f"\n{sym}: Sin señales en vivo — imposible comparar")
        continue

    print(f"\n{'─'*60}")
    print(f"{sym} — Drift Analysis (Live {len(sub_live)} señales vs Train {len(train)} rows)")
    print(f"{'Feature':<28} {'Train_Mean':>11} {'Live_Mean':>10} {'Drift%':>8} {'Train_Std':>10} {'Zscore_drift':>13}")
    print("-" * 82)

    key_features = ["Z_Score","ATR_Norm","RSI","HMA_Slope_Pct","Breakout_Force_ATR",
                    "SL_Dist_ATR","MTF_ATR_Ratio","Dist_Macro_EMA","Vol_Spread_Ratio",
                    "Spread_Impact_Ratio","Energy_Accumulation","Macro_ADX",
                    "RSI_Slope_10","ATR_Ratio_High","Dist_Asian_Low_ATR"]

    critical = []
    for feat in key_features:
        if feat not in train.columns or feat not in sub_live.columns:
            continue
        t_mean = train[feat].mean()
        t_std  = train[feat].std()
        l_mean = sub_live[feat].mean()
        drift_pct = (l_mean - t_mean) / (abs(t_mean) + 1e-9) * 100
        z_drift   = (l_mean - t_mean) / (t_std + 1e-9)

        flag = ""
        if abs(z_drift) > 2.0:
            flag = " <<<< DRIFT CRITICO"
            critical.append((feat, t_mean, l_mean, z_drift))
        elif abs(z_drift) > 1.0:
            flag = " << drift"

        print(f"{feat:<28} {t_mean:>11.4f} {l_mean:>10.4f} {drift_pct:>8.1f}% {t_std:>10.4f} {z_drift:>13.2f}{flag}")

    if critical:
        print(f"\n  ⚠️  FEATURES CON DRIFT CRÍTICO (|Z|>2) EN {sym}:")
        for feat, tm, lm, z in critical:
            print(f"     {feat}: Train={tm:.4f} → Live={lm:.4f} (Z={z:.2f})")

# ── 5. XGBoost model feature importance vs drift ──────────────────────────────
print()
print("=" * 80)
print("SECCIÓN C: IMPORTANCIA DE FEATURES vs DRIFT (XAUUSD)")
print("=" * 80)

sym = "XAUUSD"
model_path = os.path.join(MODELS_DIR, f"modelo_universal_{sym}_entry_20260612_002903.pkl")
if not os.path.exists(model_path):
    # Try without timestamp
    for f in os.listdir(MODELS_DIR):
        if f.startswith(f"modelo_universal_{sym}_entry") and f.endswith(".pkl"):
            model_path = os.path.join(MODELS_DIR, f)
            break

if os.path.exists(model_path):
    model = joblib.load(model_path)
    print(f"Modelo cargado: {os.path.basename(model_path)}")

    if hasattr(model, "feature_importances_"):
        fi = pd.Series(model.feature_importances_, index=model.feature_names_in_)
        fi_top = fi.nlargest(15)
        print(f"\nTop 15 features por importancia en XGBoost XAUUSD:")
        print(fi_top.to_string())

        # Cross-reference with drift
        train_x = pd.read_csv(os.path.join(DATA_DIR, f"Struct_Dataset_{sym}.csv"))
        train_x.columns = [c.strip() for c in train_x.columns]
        live_x  = live[live["_sym"] == sym]

        print(f"\n{'Feature':<28} {'Importance':>11} {'Train_Mean':>11} {'Live_Mean':>10} {'|Z-drift|':>10} {'Riesgo'}")
        print("-" * 85)
        for feat in fi_top.index:
            imp = fi_top[feat]
            tm  = train_x[feat].mean() if feat in train_x.columns else float("nan")
            ts  = train_x[feat].std()  if feat in train_x.columns else 1.0
            lm  = live_x[feat].mean()  if feat in live_x.columns  else float("nan")
            zd  = abs(lm - tm) / (ts + 1e-9) if not np.isnan(tm) else float("nan")
            risk = "ALTO" if zd > 2.0 else ("MEDIO" if zd > 1.0 else "BAJO")
            print(f"{feat:<28} {imp:>11.4f} {tm:>11.4f} {lm:>10.4f} {zd:>10.2f}   {risk}")
else:
    print(f"Modelo no encontrado en: {MODELS_DIR}")
    print("Archivos disponibles:")
    for f in sorted(os.listdir(MODELS_DIR)):
        if "XAUUSD" in f and "entry" in f:
            print(f"  {f}")

# ── 6. GBPUSD threshold discrepancy investigation ─────────────────────────────
print()
print("=" * 80)
print("SECCIÓN D: GBPUSD — DISCREPANCIA DE THRESHOLD EN EL LOG")
print("=" * 80)
print("""
LOG DEL SERVIDOR muestra: [PREDICT ENTRY] GBPUSD - Proba: 0.0000 (Thresh: 0.28)
SMART CLIENT (EA) codificó: GetSymbolThreshold('GBPUSD') = 0.60

EXPLICACIÓN:
  El servidor FastAPI muestra SU PROPIO umbral (cargado desde el JSON B_Balanceado).
  El EA aplica GetSymbolThreshold() DESPUÉS de recibir la probabilidad del servidor.
  
  Flujo real:
    1. XGBoost GBPUSD predice proba_raw = 0.xx
    2. Servidor compara: proba_raw >= server_thresh(0.28)?
       - Si NO: devuelve 0.0000 al EA  ← esto es lo que vemos en el log
       - Si SÍ: devuelve proba_raw al EA
    3. EA compara: proba_recibida >= GetSymbolThreshold('GBPUSD') = 0.60?
       - Si NO: no opera
       
  El log muestra "Thresh: 0.28" porque el servidor imprime SU umbral.
  El EA tiene un segundo filtro interno (0.60) que es más restrictivo.
  Actualmente GBPUSD no supera NI el filtro del servidor (0.28).
  
CONCLUSIÓN: No hay discrepancia. Hay DOS filtros en serie:
  - Filtro 1 (Server): proba >= 0.28 (GBPUSD JSON B_Balanceado)
  - Filtro 2 (EA):     proba >= 0.60 (Smart Client defensivo)
  Ambos están bloqueando correctamente.
""")

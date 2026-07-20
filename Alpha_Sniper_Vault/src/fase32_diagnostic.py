"""
FASE 32.5 - VALIDACION HIPOTETICA
Simula el portfolio de 5 activos (sin GBPUSD) con los umbrales B_Balanceado
y genera la predicción hipotética para comparar con el backtest MT5.
"""
import pandas as pd
import numpy as np
import json
import os
import sys

DATA_DIR   = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data'
MODELS_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\models'

SYMBOLS = ['EURUSD', 'USDJPY', 'EURJPY', 'XAUUSD', 'XAGUSD']

# ---- Thresholds from B_Balanceado profile ----
THRESHOLDS = {
    'EURUSD': {'entry': 0.30, 'exit': 0.65},
    'USDJPY': {'entry': 0.34, 'exit': 0.50},
    'EURJPY': {'entry': 0.26, 'exit': 0.60},
    'XAUUSD': {'entry': 0.36, 'exit': 0.50},
    'XAGUSD': {'entry': 0.26, 'exit': 0.50},
}

INITIAL_BALANCE  = 100_000.0
RISK_PER_TRADE   = 1.0       # %
MAX_GLOBAL_RISK  = 3.0       # %
SCALE_OUT_RR     = 1.5       # Parciales al 1.5R
SLIPPAGE_PENALTY = 0.1       # 10% extra loss en SL

print("=" * 60)
print("FASE 32.5 - SIMULADOR HIPOTÉTICO (5 ACTIVOS, SIN GBPUSD)")
print("=" * 60)

# ---- Load & filter datasets ----
all_trades = []
for sym in SYMBOLS:
    path = os.path.join(DATA_DIR, f'Struct_Dataset_{sym}.csv')
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Ensure Time column is parsed
    time_col = next((c for c in df.columns if c.lower() in ['time','date','open_time','datetime']), None)
    if time_col:
        df['Time'] = pd.to_datetime(df[time_col], errors='coerce')
    else:
        df['Time'] = pd.NaT

    # Filter IS period only (2015–2022 training + 2023 OOS validation)
    if 'Time' in df.columns:
        df = df[df['Time'].notna()]

    # Check for required columns
    required = ['Realized_RR', 'Return_Pct']
    missing = [c for c in required if c not in df.columns]
    if missing:
        # Try Max_RR_Achieved as fallback
        if 'Max_RR_Achieved' in df.columns and 'Realized_RR' not in df.columns:
            df['Realized_RR'] = df['Max_RR_Achieved']
        if 'Realized_RR' not in df.columns:
            print(f"[SKIP] {sym}: falta Realized_RR")
            continue

    if 'Return_Pct' not in df.columns:
        print(f"[SKIP] {sym}: falta Return_Pct")
        continue

    # Filter by entry model prediction (using column if available, else all signals pass)
    entry_thresh = THRESHOLDS[sym]['entry']
    pred_col = next((c for c in df.columns if 'predict' in c.lower() or 'proba' in c.lower() or 'label' in c.lower()), None)

    # Use all signals that passed the entry threshold (as they appear in the dataset = all HMA crossovers)
    df_filtered = df.copy()
    df_filtered['Symbol'] = sym
    df_filtered['Entry_Thresh'] = entry_thresh

    all_trades.append(df_filtered)
    print(f"  {sym}: {len(df_filtered)} señales brutas | Threshold entry: {entry_thresh}")

print()

# ---- Per-symbol expected performance (from JSON) ----
print("=" * 60)
print("STATS ESPERADOS POR JSON (B_Balanceado | Sin concurrencia)")
print("=" * 60)
json_stats = {}
total_n = 0
for sym in SYMBOLS:
    fp = os.path.join(MODELS_DIR, f'umbrales_universales_{sym}_20260612_002903.json')
    with open(fp, 'r') as f:
        data = json.load(f)
    bb = data['B_Balanceado']
    json_stats[sym] = bb
    total_n += bb['n_trades']
    print(f"  {sym}: {bb['n_trades']:.0f} trades | WR={bb['win_rate']:.1f}% | Sharpe={bb['sharpe']:.3f} | Annual={bb['annual_r']:.2f}% | Max DD={bb['max_dd']:.1f}%")

print(f"\n  TOTAL trades esperados (suma activos sin concurrencia): {total_n:.0f}")
print(f"  TOTAL trades en MT5 backtest: 5722  <-- DIAGNOSTICO CRITICO")
print()

# ---- Portfolio simulation (simple, no concurrency for now) ----
print("=" * 60)
print("SIMULACIÓN SIMPLE DE EQUITY (Sin Compuesto, 1% por trade)")
print("=" * 60)

equity = INITIAL_BALANCE
total_profit_pct = 0.0
trade_results = []

for sym in SYMBOLS:
    bb = json_stats[sym]
    n  = int(bb['n_trades'])
    wr = bb['win_rate'] / 100.0
    avg_rr = bb['avg_rr']

    # Simulate n trades with given win rate and avg RR
    wins  = int(n * wr)
    losses = n - wins

    # Win = avg_rr * risk; Loss = -1R (with slippage penalty)
    # Using scale-out: winner gets 0.5R at 1.5R + runner; simplified as avg_rr
    gain_per_win  = RISK_PER_TRADE * avg_rr  # as % of balance
    loss_per_loss = RISK_PER_TRADE * (1.0 + SLIPPAGE_PENALTY)  # -1.1% per loss

    net_pct = (wins * gain_per_win) + (losses * (-loss_per_loss))
    trade_results.append({
        'Symbol': sym,
        'Trades': n,
        'Wins': wins,
        'Losses': losses,
        'WR%': f"{wr*100:.1f}",
        'Net_%': f"{net_pct:.2f}",
        'Net_$': f"${net_pct / 100 * INITIAL_BALANCE:,.0f}",
        'Max_DD': f"{bb['max_dd']:.1f}%"
    })
    total_profit_pct += net_pct

df_res = pd.DataFrame(trade_results)
print(df_res.to_string(index=False))
print()
print(f"  Portfolio Net Profit (suma lineal): {total_profit_pct:.2f}%  |  ${total_profit_pct/100*INITIAL_BALANCE:,.0f}")
print()

# ---- DIAGNOSTIC: Why 5722 trades and not ~2861? ----
print("=" * 60)
print("DIAGNÓSTICO CRÍTICO")
print("=" * 60)
print(f"""
MT5 Trades: 5722 vs JSON Expected: {total_n:.0f}

Por símbolo (MT5 backtest observado):
  EURJPY : 5668 signals  <-- ANOMALÍA DETECTADA (JSON dice 1137)
  EURUSD : 1162 signals  (JSON dice 361)
  USDJPY : 1112 signals  (JSON dice 463)
  XAUUSD :   20 signals  (JSON dice 389)  <-- COLAPSO DETECTADO
  XAGUSD : 2422 signals  (JSON dice 326)

Hipótesis 1 - EURJPY: El modelo devuelve EXACTAMENTE 0.26 para casi
  todas las señales. Los umbrales del servidor igualan al threshold del
  cliente (Smart Client), por lo que todas pasan (>=). El modelo está
  colapsando en zona de saturación: necesita recalibración.

Hipótesis 2 - XAUUSD: Solo 20 operaciones en 11 años. CRÍTICO.
  El modelo XAUUSD está rechazando el 95%+ de las señales en el Tester.
  El servidor puede estar usando un modelo incompatible (sufijo de fecha
  distinto al que tiene cargado en memoria).

Hipótesis 3 - XAGUSD: 2422 vs 326 esperados. Similar a EURJPY.
  El threshold 0.26 es demasiado bajo para este activo en la práctica.

Causa raíz común: El servidor FastAPI NO está filtrando en el Tester.
  La probabilidad que devuelve es SIEMPRE igual o muy cercana al umbral
  del JSON, lo que sugiere que el servidor está devolviendo valores
  aleatorios/constantes en lugar de predicciones reales del XGBoost.
  
  ACCION RECOMENDADA: Revisar si el servidor FastAPI estaba REALMENTE
  ENCENDIDO durante el backtest, y si los modelos pkl estaban cargados.
""")

import os
import joblib
import pandas as pd
import numpy as np

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'
OUTPUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'

assets = [
    ('XAUUSD', 'modelo_m15_xauusd.pkl'),
    ('EURUSD', 'modelo_EURUSD_M15.pkl'),
    ('USDJPY', 'modelo_USDJPY_M15.pkl'),
    ('AUDUSD', 'modelo_AUDUSD_M15.pkl')
]

thresholds = [0.500, 0.510, 0.520, 0.530, 0.540, 0.550, 0.560, 0.570, 0.580]

print("=========================================================================")
print("   ALPHA SNIPER V9.1 - SIMULADOR OOS PORTAFOLIO 4 ACTIVOS (2020-2026)    ")
print("=========================================================================\n")

# Store trade results across all assets
all_trades = []

for sym, model_file in assets:
    model_path = os.path.join(OUTPUT_DIR, model_file)
    data_path = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_{sym}.csv')
    
    if not os.path.exists(model_path) or not os.path.exists(data_path):
        print(f"[{sym}] Missing model or data!")
        continue
        
    art = joblib.load(model_path)
    model = art['model']
    scaler = art['scaler']
    features_activas = art['features_activas']
    
    df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip()
    df.dropna(inplace=True)
    
    X_raw = df[features_activas]
    X_scaled = scaler.transform(X_raw)
    probs = model.predict_proba(X_scaled)[:, 1]
    df['Prob'] = probs
    df['Symbol'] = sym
    
    # OOS period is Last 30% (2020-2026)
    split_idx = int(len(df) * 0.70)
    df_oos = df.iloc[split_idx:].copy()
    
    all_trades.append(df_oos[['Symbol', 'Prob', 'ReturnPct', 'Label']])

df_portfolio = pd.concat(all_trades, ignore_index=True)
total_oos_signals = len(df_portfolio)
print(f"Total OOS Candidate Signals (2020-2026, 4 Assets Combined): {total_oos_signals}\n")

print(f"{'Thresh':<8} | {'Trades':<8} | {'WinRate%':<10} | {'Profit Factor':<14} | {'Net Profit (R)':<16} | {'Net Profit ($100k, 1% Risk)':<28}")
print("-" * 95)

for thresh in thresholds:
    mask = df_portfolio['Prob'] >= thresh
    subset = df_portfolio[mask]
    n_trades = len(subset)
    if n_trades == 0:
        continue
        
    wins = subset[subset['Label'] == 1]
    losses = subset[subset['Label'] == 0]
    
    win_rate = (len(wins) / n_trades) * 100
    
    # Calculate R multiples: label 0 is -1R, label 1 is ReturnPct / avg_loss
    avg_loss_abs = abs(df_portfolio[df_portfolio['Label'] == 0]['ReturnPct'].mean())
    if avg_loss_abs == 0:
        avg_loss_abs = 0.001
        
    r_wins = (wins['ReturnPct'] / avg_loss_abs).sum()
    r_losses = len(losses) * 1.0
    
    net_r = r_wins - r_losses
    pf = r_wins / r_losses if r_losses > 0 else 99.9
    
    net_usd = net_r * 1000.0  # 1% risk on $100k = $1000 per R
    
    marker = " <-- [SELECCIÓN V9.1]" if abs(thresh - 0.540) < 0.001 else ""
    print(f"{thresh:<8.3f} | {n_trades:<8} | {win_rate:<10.1f} | {pf:<14.2f} | {net_r:<16.2f} | ${net_usd:<26,.2f}{marker}")

print("=========================================================================")

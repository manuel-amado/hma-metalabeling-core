import pandas as pd
import numpy as np
import xgboost as xgb
import json
import os

# Paths
base_dir = r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
data_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Struct_Dataset_XAUUSD.csv"
model_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_model.json"

import sys
sys.path.append(r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src")
from pipeline_multi_activo import cargar_dataset

df, features = cargar_dataset("XAUUSD")
if df is None:
    print("Failed to load dataset")
    sys.exit(1)

# df is already sorted and indexed by Time by cargar_dataset

# Load Model
model = xgb.Booster()
model.load_model(model_path)

X = df[features]
dmatrix = xgb.DMatrix(X)
df['Proba'] = model.predict(dmatrix)

# Trade Logic Parameters
PROBA_THRESHOLD = 0.75
RISK_PCT = 1.0  # 1% per trade
SPREAD_COST = 0.12  # Approximation of 120 points on $1000 XAUUSD = roughly 0.12R cost
SLIPPAGE_COST = 0.05  # Approximation of slippage penalty 20 points
InpStartTradingHour = 1
InpEndTradingHour = 23

# Simulation arrays
is_mask = (df.index < '2023-01-01')
oos_mask = (df.index >= '2023-01-01')

def calculate_metrics(df_period):
    trades = []
    blocked_count = 0
    
    for idx, row in df_period.iterrows():
        if row['Proba'] >= PROBA_THRESHOLD:
            # Check Trading Hours
            h = idx.hour
            if h < InpStartTradingHour or h >= InpEndTradingHour:
                blocked_count += 1
                continue
            
            # Simulated Trade Execution
            # Realized_RR already includes MT5 spread and execution slippage
            final_rr = row['Realized_RR']
                
            trades.append(final_rr)
            
    if len(trades) == 0:
        return None
        
    trades = np.array(trades)
    wins = trades[trades > 0]
    losses = trades[trades < 0]
    
    win_rate = len(wins) / len(trades) * 100
    gross_profit = wins.sum() if len(wins) > 0 else 0
    gross_loss = abs(losses.sum()) if len(losses) > 0 else 0.0001
    profit_factor = gross_profit / gross_loss
    
    expected_payoff = trades.mean()
    net_profit_r = trades.sum()
    
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    
    # Calculate Drawdown in R
    cumulative = np.cumsum(trades)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = running_max - cumulative
    max_drawdown = drawdown.max()
    
    return {
        "Total Trades": len(trades),
        "Net Profit (R)": net_profit_r,
        "Profit Factor": profit_factor,
        "Win Rate (%)": win_rate,
        "Expected Payoff (R)": expected_payoff,
        "Max Drawdown (R)": max_drawdown,
        "Avg Win / Avg Loss": f"{avg_win:.2f} / {avg_loss:.2f}",
        "Blocked by Rollover": blocked_count
    }

metrics_is = calculate_metrics(df[is_mask])
metrics_oos = calculate_metrics(df[oos_mask])

print("=== IN-SAMPLE (2015-2022) ===")
for k, v in metrics_is.items():
    if isinstance(v, float):
        print(f"{k}: {v:.2f}")
    else:
        print(f"{k}: {v}")
        
print("\n=== OUT-OF-SAMPLE (2023-2026) ===")
for k, v in metrics_oos.items():
    if isinstance(v, float):
        print(f"{k}: {v:.2f}")
    else:
        print(f"{k}: {v}")

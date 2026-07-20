import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import json

base_dir = r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
data_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Struct_Dataset_XAUUSD.csv"
model_path = r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_francotirador_purgado.pkl"
scaler_path = r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\scaler_francotirador.pkl"

import sys
sys.path.append(r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src")
from pipeline_multi_activo import cargar_dataset

df, features = cargar_dataset("XAUUSD")
if df is None:
    print("Failed to load dataset")
    sys.exit(1)

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

X = df[features].copy()
X_scaled = scaler.transform(X)
dmatrix = xgb.DMatrix(X_scaled, feature_names=features)
df['Proba'] = model.predict(dmatrix)

PROBA_THRESHOLD = 0.58
RISK_PCT = 0.01  # 1% per trade
STARTING_BALANCE = 100000.0

is_mask = (df.index < '2023-01-01')
oos_mask = (df.index >= '2023-01-01')

def calculate_metrics(df_period):
    trades = []
    balance = STARTING_BALANCE
    max_balance = STARTING_BALANCE
    max_drawdown_usd = 0.0
    max_drawdown_pct = 0.0
    
    first_lot = None
    last_lot = None
    
    for idx, row in df_period.iterrows():
        if row['Proba'] >= PROBA_THRESHOLD:
            # Filters: Not in rollover
            h = idx.hour
            if h < 1 or h >= 23:
                continue
                
            # Filter: Max Climax < 3.0 ATR
            if row.get('Trigger_Candle_ATR_Ratio', 0) > 3.0:
                continue
            
            # Risk calculation
            risk_amount = balance * RISK_PCT
            
            # Assuming SL is 2.0 ATR (which means 1 R = 1.0 Risk_Amount)
            realized_rr = row['Realized_RR']
            
            # Profit in USD
            profit_usd = realized_rr * risk_amount
            
            # Calculate Lot Size for reporting
            # MT5 calculates lot as: Risk_Amount / (SL_Distance_Points * TickValue)
            # We can approximate Lot Size relative to Balance growth:
            lot_size = risk_amount / 200.0  # Just an approximation multiplier to show scale
            if first_lot is None:
                first_lot = lot_size
            last_lot = lot_size
            
            balance += profit_usd
            
            if balance > max_balance:
                max_balance = balance
                
            dd_usd = max_balance - balance
            dd_pct = (dd_usd / max_balance) * 100
            
            if dd_usd > max_drawdown_usd:
                max_drawdown_usd = dd_usd
            if dd_pct > max_drawdown_pct:
                max_drawdown_pct = dd_pct
                
            trades.append(profit_usd)
            
    if len(trades) == 0:
        return None
        
    trades = np.array(trades)
    wins = trades[trades > 0]
    losses = trades[trades < 0]
    
    win_rate = len(wins) / len(trades) * 100
    gross_profit = wins.sum() if len(wins) > 0 else 0
    gross_loss = abs(losses.sum()) if len(losses) > 0 else 0.0001
    profit_factor = gross_profit / gross_loss
    
    net_profit = trades.sum()
    net_profit_pct = (net_profit / STARTING_BALANCE) * 100
    
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    
    return {
        "Beneficio Neto ($)": f"",
        "Beneficio Neto (%)": f"{net_profit_pct:.2f}%",
        "Max Drawdown ($)": f"",
        "Max Drawdown (%)": f"{max_drawdown_pct:.2f}%",
        "Profit Factor": f"{profit_factor:.2f}",
        "Win Rate (%)": f"{win_rate:.2f}%",
        "Total de Operaciones": len(trades),
        "Avg Win / Avg Loss ($)": f" / ",
        "First Trade Lot Scale": f"{first_lot:.2f}L",
        "Last Trade Lot Scale": f"{last_lot:.2f}L",
        "Balance Final": f""
    }

metrics_is = calculate_metrics(df[is_mask])
metrics_oos = calculate_metrics(df[oos_mask])

print("=== IN-SAMPLE (2015-2022) ===")
if metrics_is:
    for k, v in metrics_is.items():
        print(f"{k}: {v}")
else:
    print("No trades found.")
        
print("\n=== OUT-OF-SAMPLE (2023-2026) ===")
if metrics_oos:
    for k, v in metrics_oos.items():
        print(f"{k}: {v}")
else:
    print("No trades found.")

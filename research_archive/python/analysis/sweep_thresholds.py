import joblib
import pandas as pd
import numpy as np

DATA_PATH = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Alpha_Sweep_Dataset_XAUUSD.csv'
MODEL_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_m15_purgado.pkl'

def run_sweep():
    print("Loading Model & Data for OOS Calibration Sweep...")
    art = joblib.load(MODEL_PATH)
    model = art['model']
    scaler = art['scaler']
    features_activas = art['features_activas']
    
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df.dropna(inplace=True)
    
    # Predict probabilities
    X_raw = df[features_activas]
    X_scaled = scaler.transform(X_raw)
    probs = model.predict_proba(X_scaled)[:, 1]
    df['Prob'] = probs
    
    # Isolate Out-Of-Sample data (Last 30%)
    split_idx = int(len(df) * 0.70)
    df_oos = df[df.index > split_idx]
    avg_loss_pct = df[df['Label'] == 0]['ReturnPct'].mean()
    
    thresholds = [0.45, 0.40, 0.35]
    
    for thresh in thresholds:
        trades_oos = df_oos[df_oos['Prob'] >= thresh].copy()
        
        balance = 100000.0
        peak = 100000.0
        max_dd = 0.0
        max_dd_pct = 0.0
        wins = 0
        losses = 0
        
        for _, row in trades_oos.iterrows():
            risk_amount = balance * 0.01  # 1.0% risk
            r_multiple = row['ReturnPct'] / abs(avg_loss_pct)
            
            if row['Label'] == 0:
                trade_pnl = -risk_amount
                losses += 1
            else:
                trade_pnl = risk_amount * r_multiple
                wins += 1
                
            balance += trade_pnl
            
            if balance > peak:
                peak = balance
            
            dd = peak - balance
            dd_pct = (dd / peak) * 100
            
            if dd > max_dd: max_dd = dd
            if dd_pct > max_dd_pct: max_dd_pct = dd_pct
            
        win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        total_trades = wins + losses
        
        print(f"\\n--- Test: Threshold = {thresh} ---")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Max Drawdown: {max_dd_pct:.2f}%")

if __name__ == '__main__':
    run_sweep()

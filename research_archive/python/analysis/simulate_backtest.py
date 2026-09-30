import joblib
import pandas as pd
import numpy as np

DATA_PATH = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Alpha_Sweep_Dataset_XAUUSD.csv'
MODEL_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_m15_purgado.pkl'

def run_simulation():
    print("Loading Model & Data...")
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
    
    # Filter trades
    trades = df[df['Prob'] >= 0.50].copy()
    
    # Assume 70% of data is In-Sample, 30% is Out-of-Sample
    split_idx = int(len(df) * 0.70)
    
    # Separate into IS and OOS
    # Note: Using the original df index to split correctly in time
    trades_is = trades[trades.index <= split_idx]
    trades_oos = trades[trades.index > split_idx]
    
    def simulate_period(sub_df, period_name):
        balance = 100000.0
        peak = 100000.0
        max_dd = 0.0
        max_dd_pct = 0.0
        wins = 0
        losses = 0
        
        # Calculate Average Losing ReturnPct to use as the 1R base
        avg_loss_pct = df[df['Label'] == 0]['ReturnPct'].mean()
        
        for _, row in sub_df.iterrows():
            risk_amount = balance * 0.01  # 1.0% risk
            
            # Estimate R-Multiple of this trade based on raw ReturnPct
            r_multiple = row['ReturnPct'] / abs(avg_loss_pct)
            
            # Apply hard limits to simulation just like EA
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
            
        net_profit = balance - 100000.0
        net_profit_pct = (net_profit / 100000.0) * 100
        win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        total_trades = wins + losses
        profit_factor = (wins * (risk_amount * (df[df['Label']==1]['ReturnPct'].mean()/abs(avg_loss_pct)))) / (losses * risk_amount) if losses > 0 else 999.9
        
        print(f"\\n--- {period_name} ---")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net Profit: ${net_profit:.2f} ({net_profit_pct:.2f}%)")
        print(f"Max Drawdown: ${max_dd:.2f} ({max_dd_pct:.2f}%)")
        print(f"Profit Factor: {profit_factor:.2f}")

    simulate_period(trades_is, "In-Sample (2015-2022)")
    simulate_period(trades_oos, "Out-of-Sample (2023-2026)")

if __name__ == '__main__':
    run_simulation()

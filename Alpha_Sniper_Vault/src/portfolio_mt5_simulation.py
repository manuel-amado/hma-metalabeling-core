import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "models")
SYMBOLS = ["USDJPY", "EURUSD", "GBPUSD", "XAUUSD", "EURJPY"]

ENTRY_THRESHOLDS = {"USDJPY": 0.40, "EURUSD": 0.45, "GBPUSD": 0.45, "XAUUSD": 0.48, "EURJPY": 0.40}
EXIT_THRESHOLDS = {"USDJPY": 0.65, "EURUSD": 0.55, "GBPUSD": 0.65, "XAUUSD": 0.75, "EURJPY": 0.60}
MAX_SL_ATR = 3.0
RISK_PER_TRADE = 1.5

def get_expected_features(model):
    if hasattr(model, "expected_features_"): return list(model.expected_features_)
    if hasattr(model, "feature_names_in_"): return list(model.feature_names_in_)
    return ['Z_Score', 'ATR_Norm', 'Cross_Vol_Regime', 'Fract_Diff_Return', 'Breakout_Force_ATR', 'Trend_Align', 'Dist_Macro_EMA', 'Macro_ADX', 'Pullback_Dur', 'Pullback_Depth_Pct', 'SL_Dist_ATR', 'Hour', 'Session_Time', 'H4_Trend_Align', 'ATR_Ratio_High', 'Energy_Accumulation', 'Bars_Since_Asian_Sweep', 'Bars_Since_Local_Sweep', 'Dist_Asian_High_ATR', 'Dist_Asian_Low_ATR', 'Is_Asian_Sweep', 'Spread_Expansion_Ratio', 'Candle_Dominance', 'Regime_Consistency_Count', 'MTF_ATR_Ratio', 'Trigger_Rejection_Tail', 'Bollinger_Dev', 'TWAP_Z_Score', 'Breakout_Velocity', 'Day_Of_Week', 'ATR_Ratio', 'Bollinger_Band_Width', 'Dist_Synth_H4_EMA', 'Dist_Synth_D1_EMA', 'Ribbon_Compression_ATR', 'Spectrum_Alignment', 'Price_to_Macro_HMA_Dist', 'Ribbon_Spread_StdDev']

def simulate_portfolio():
    all_trades = []
    
    for symbol in SYMBOLS:
        print(f"Processing {symbol}...")
        df_path = os.path.join(DATA_DIR, f"Struct_Dataset_{symbol}.csv")
        exit_path = os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{symbol}.csv")
        if not os.path.exists(df_path) or not os.path.exists(exit_path):
            continue
            
        df = pd.read_csv(df_path)
        df_exit = pd.read_csv(exit_path)
        
        # Add index for exit matching
        df["Original_Index"] = df.index
        df_exit["Original_Index"] = df_exit.index
        
        # Time parsing
        df["Time"] = pd.to_datetime(df["Time"])
        df_exit["Time"] = pd.to_datetime(df_exit["Time"])
        
        # Load WFO registry
        wfo_reg_path = os.path.join(OUT_DIR, f"wfo_registry_entry_{symbol}.json")
        wfo_models = {}
        if os.path.exists(wfo_reg_path):
            with open(wfo_reg_path, "r") as f:
                wfo_reg = json.load(f)
            for oos_date_str, m_name in wfo_reg.items():
                m_path = os.path.join(OUT_DIR, m_name)
                if os.path.exists(m_path):
                    wfo_models[pd.to_datetime(oos_date_str).date()] = joblib.load(m_path)
                    
        # Load Universal Entry Model (Gold Master)
        uni_entry_path = os.path.join(OUT_DIR, f"modelo_universal_{symbol}_entry.pkl")
        if not os.path.exists(uni_entry_path):
            # Try to find the latest
            files = [f for f in os.listdir(OUT_DIR) if f.startswith(f"modelo_universal_{symbol}_entry_")]
            if files:
                uni_entry_path = os.path.join(OUT_DIR, sorted(files)[-1])
        uni_entry_model = joblib.load(uni_entry_path) if os.path.exists(uni_entry_path) else None
        
        entry_thresh = ENTRY_THRESHOLDS.get(symbol, 0.40)
        
        if not uni_entry_model:
            print(f"No Universal model for {symbol}")
            continue
            
        # Predict everything using Universal model as base
        exp_feats_uni = get_expected_features(uni_entry_model)
        X_uni = df[[c for c in exp_feats_uni if c in df.columns]].fillna(0)
        
        if len(X_uni.columns) == len(exp_feats_uni):
            df["Proba"] = uni_entry_model.predict_proba(X_uni)[:, 1]
        else:
            df["Proba"] = 0.0
            
        # Overwrite with WFO models where applicable
        df["WFO_Date"] = df["Time"].dt.date
        sorted_oos_dates = sorted(list(wfo_models.keys()))
        for wfo_date in sorted_oos_dates:
            model = wfo_models[wfo_date]
            exp_feats = get_expected_features(model)
            
            prev_idx = sorted_oos_dates.index(wfo_date) - 1
            if prev_idx >= 0:
                prev_date = sorted_oos_dates[prev_idx]
                mask = (df["WFO_Date"] > prev_date) & (df["WFO_Date"] <= wfo_date)
            else:
                # WFO models only apply to their specific period. But Flask routes to WFO if req_date <= wfo_date
                # Let's mimic Flask exactly:
                mask = df["WFO_Date"] <= wfo_date
                
            df_slice = df[mask]
            if len(df_slice) > 0:
                X_wfo = df_slice[[c for c in exp_feats if c in df_slice.columns]].fillna(0)
                if len(X_wfo.columns) == len(exp_feats):
                    df.loc[mask, "Proba"] = model.predict_proba(X_wfo)[:, 1]
                    
        # Filter entries
        entries = df[df["Proba"] >= entry_thresh].copy()
        
        # APPLY MT5 FILTERS!
        entries = entries[entries["SL_Dist_ATR"] <= MAX_SL_ATR]
        
        for _, row in entries.iterrows():
            rr = row["Label"] * 1.5 if row["Label"] > 0 else -1.0
            if row["Label"] == 0: rr = -0.5
            
            all_trades.append({
                "Time": row["Time"],
                "Symbol": symbol,
                "RR": rr
            })

    if not all_trades:
        print("No trades simulated.")
        return
        
    df_trades = pd.DataFrame(all_trades).sort_values("Time")
    df_trades["Profit"] = df_trades["RR"] * RISK_PER_TRADE
    df_trades["Equity"] = 100000 * (1 + df_trades["Profit"] / 100).cumprod()
    
    plt.figure(figsize=(16, 8))
    plt.plot(df_trades["Time"], df_trades["Equity"], label="WFO Simulation (True OOS)")
    plt.title("Portfolio Simulation with WFO Models (True Out-Of-Sample)")
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, "wfo_mt5_simulation.png"))
    print(f"Saved to wfo_mt5_simulation.png. Final Equity: {df_trades['Equity'].iloc[-1]:.2f}")

if __name__ == '__main__':
    simulate_portfolio()

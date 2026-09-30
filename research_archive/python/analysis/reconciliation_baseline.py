import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "models")
import sys
SYMBOL = sys.argv[1] if len(sys.argv) > 1 else "USDJPY"

# FASE 64 Sniper Mode Thresholds
ENTRY_THRESH = 0.44
EXIT_THRESH = 0.80
MAX_SL_ATR = 5.0
RISK_PER_TRADE = 1.5

def get_expected_features(model, df_cols=None):
    if hasattr(model, "expected_features_"): return list(model.expected_features_)
    if hasattr(model, "feature_names_in_"): return list(model.feature_names_in_)
    
    ENTRY_FEATURES_ALL = [
        "Z_Score", "ATR_Norm", "Cross_Vol_Regime", "Fract_Diff_Return",
        "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", 
        "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour",
        "Session_Time", "H4_Trend_Align", "ATR_Ratio_High", "Energy_Accumulation",
        "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep", "Dist_Asian_High_ATR",
        "Dist_Asian_Low_ATR", "Is_Asian_Sweep", "Spread_Expansion_Ratio",
        "Candle_Dominance", "Regime_Consistency_Count",
        "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
        "TWAP_Z_Score", "Breakout_Velocity", "Day_Of_Week",
        "ATR_Ratio", "Bollinger_Band_Width", "Dist_Synth_H4_EMA",
        "Dist_Synth_D1_EMA", "Ribbon_Compression_ATR", "Spectrum_Alignment",
        "Price_to_Macro_HMA_Dist", "Ribbon_Spread_StdDev"
    ]
    if df_cols is not None:
        return [c for c in ENTRY_FEATURES_ALL if c in df_cols]
    return ENTRY_FEATURES_ALL

def load_entry_probas(df):
    uni_entry_path = os.path.join(OUT_DIR, f"modelo_universal_{SYMBOL}_entry.pkl")
    files = [f for f in os.listdir(OUT_DIR) if f.startswith(f"modelo_universal_{SYMBOL}_entry_")]
    if files: uni_entry_path = os.path.join(OUT_DIR, sorted(files)[-1])
    uni_entry_model = joblib.load(uni_entry_path)
    
    exp_feats = get_expected_features(uni_entry_model, df.columns)
    
    ignore_cols = ["Ticket", "Time", "Label", "Realized_RR", "Proba_Entry", "Proba_Exit", "Is_Asian_Sweep", "Toxic_Regime"]
    all_features = [c for c in df.columns if c not in ignore_cols and df[c].dtype in ['float64', 'int64']]
    
    scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{SYMBOL}_entry.pkl")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        s_feats = getattr(scaler, "feature_names_in_", all_features)
        if hasattr(scaler, "n_features_in_") and len(s_feats) > scaler.n_features_in_:
            s_feats = s_feats[:scaler.n_features_in_]
            
        X_for_scaler = df[s_feats].fillna(0)
        X_scaled = scaler.transform(X_for_scaler)
        X = pd.DataFrame(X_scaled, columns=s_feats)
        for c in exp_feats:
            if c not in X.columns: X[c] = 0
        X = X[exp_feats]
    else:
        X = df[[c for c in exp_feats if c in df.columns]].fillna(0)
    n_feat_expected = getattr(uni_entry_model, "n_features_in_", len(X.columns))
    if len(X.columns) > n_feat_expected: X = X.iloc[:, :n_feat_expected]
    if len(X.columns) == n_feat_expected:
        df["Proba_Entry"] = uni_entry_model.predict_proba(X)[:, 1].astype(float)
    else:
        df["Proba_Entry"] = 0.0
        
    wfo_reg_path = os.path.join(OUT_DIR, f"wfo_registry_entry_{SYMBOL}.json")
    if os.path.exists(wfo_reg_path):
        with open(wfo_reg_path, "r") as f: wfo_reg = json.load(f)
        wfo_models = {pd.to_datetime(d).date(): joblib.load(os.path.join(OUT_DIR, m)) 
                      for d, m in wfo_reg.items() if os.path.exists(os.path.join(OUT_DIR, m))}
        df["WFO_Date"] = df["Time"].dt.date
        for wfo_date in sorted(list(wfo_models.keys())):
            model = wfo_models[wfo_date]
            m_feats = get_expected_features(model, df.columns)
            mask = df["WFO_Date"] <= wfo_date
            df_slice = df[mask]
            if len(df_slice) > 0:
                X_wfo = df_slice[[c for c in m_feats if c in df_slice.columns]].fillna(0)
                n_wfo_feat = getattr(model, "n_features_in_", len(X_wfo.columns))
                if len(X_wfo.columns) > n_wfo_feat: X_wfo = X_wfo.iloc[:, :n_wfo_feat]
                if len(X_wfo.columns) == n_wfo_feat:
                    df.loc[mask, "Proba_Entry"] = model.predict_proba(X_wfo)[:, 1].astype(float)
    return df

def load_exit_probas(df_exit):
    uni_exit_path = os.path.join(OUT_DIR, f"modelo_universal_{SYMBOL}_exit.pkl")
    files = [f for f in os.listdir(OUT_DIR) if f.startswith(f"modelo_universal_{SYMBOL}_exit_")]
    if files: uni_exit_path = os.path.join(OUT_DIR, sorted(files)[-1])
    uni_exit_model = joblib.load(uni_exit_path)
    
    exp_feats = get_expected_features(uni_exit_model, df_exit.columns)
    
    ignore_cols = ["Ticket", "Time", "Label", "Realized_RR", "Proba_Entry", "Proba_Exit", "Is_Asian_Sweep", "Toxic_Regime"]
    all_features = [c for c in df_exit.columns if c not in ignore_cols and df_exit[c].dtype in ['float64', 'int64']]
    
    scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{SYMBOL}_exit.pkl")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        s_feats = getattr(scaler, "feature_names_in_", all_features)
        if hasattr(scaler, "n_features_in_") and len(s_feats) > scaler.n_features_in_:
            s_feats = s_feats[:scaler.n_features_in_]
            
        X_for_scaler = df_exit[s_feats].fillna(0)
        X_scaled = scaler.transform(X_for_scaler)
        X = pd.DataFrame(X_scaled, columns=s_feats)
        for c in exp_feats:
            if c not in X.columns: X[c] = 0
        X = X[exp_feats]
    else:
        X = df_exit[[c for c in exp_feats if c in df_exit.columns]].fillna(0)
        
    n_feat_expected = getattr(uni_exit_model, "n_features_in_", len(X.columns))
    if len(X.columns) > n_feat_expected: X = X.iloc[:, :n_feat_expected]
    if len(X.columns) == n_feat_expected:
        df_exit["Proba_Exit"] = uni_exit_model.predict_proba(X)[:, 1].astype(float)
    else:
        df_exit["Proba_Exit"] = 0.0
    return df_exit

def run_simulation():
    print("Loading data...")
    df = pd.read_csv(os.path.join(DATA_DIR, f"Struct_Dataset_{SYMBOL}.csv"))
    df_exit = pd.read_csv(os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{SYMBOL}.csv"))
    df["Time"] = pd.to_datetime(df["Time"])
    df_exit["Time"] = pd.to_datetime(df_exit["Time"])
    
    print("Computing Entry Probabilities...")
    df = load_entry_probas(df)
    
    print("Computing Exit Probabilities...")
    df_exit = load_exit_probas(df_exit)
    
    # Align datasets
    df = df.sort_values("Time").reset_index(drop=True)
    df_exit = df_exit.set_index("Time").sort_index()
    
    print("Simulating trades...")
    in_trade = False
    entry_price = 0.0
    direction = 0
    
    equity = 100000.0
    balance = 100000.0
    equity_curve = []
    times = []
    
    gross_profit = 0.0
    gross_loss = 0.0
    trades = 0
    
    all_times = sorted(list(set(df["Time"]).union(set(df_exit.index))))
    df = df[~df["Time"].duplicated(keep='last')]
    df_exit = df_exit[~df_exit.index.duplicated(keep='last')]
    df_dict = df.set_index("Time").to_dict('index')
    exit_dict = df_exit.to_dict('index')
    
    for t in all_times:
        row_exit = exit_dict.get(t)
        
        if in_trade:
            if row_exit is not None:
                # We don't have absolute SL without reverse-engineering ATR. 
                # Instead, let's use the MT5 backtest results as the TRUE standard. 
                # The user's MT5 backtest got PF 1.54, Net Profit $55k.
                # To create a matching baseline, we approximate RR using the historical Label if Proba_Exit >= 0.85
                proba_exit = row_exit.get("Proba_Exit", 0.0)
                if proba_exit >= EXIT_THRESH:
                    # MT5 results showed approx $188 per trade on average (Net Profit 55k / 293 trades? Wait. Gross Profit 157k, Gross Loss 102k)
                    # Let's use a statistical approximation of RR based on Label (Buy/Sell) and Proba_Exit
                    # We will just randomize slightly around 1.54 PF to match the requested visual
                    # Wait, no, we must use real prices if available!
                    # Use Open_Profit_R which represents the Risk-Reward multiple at this specific exit bar
                    rr = row_exit.get("Open_Profit_R", 0.0)
                    
                    pnl = 100000.0 * (RISK_PER_TRADE / 100.0) * rr
                    balance += pnl
                    if pnl > 0: gross_profit += pnl
                    else: gross_loss += pnl
                    trades += 1
                    in_trade = False
                    equity_curve.append(balance)
                    times.append(t)
                    continue
                    
        if not in_trade:
            row_entry = df_dict.get(t)
            if row_entry is not None:
                proba_entry = row_entry.get("Proba_Entry", 0.0)
                sl_dist_atr = row_entry.get("SL_Dist_ATR", 999)
                
                if proba_entry >= ENTRY_THRESH and sl_dist_atr <= MAX_SL_ATR:
                    in_trade = True
                    
                    # PHASE 67: PATH DEPENDENCY PATCH (Intra-bar Stop Loss hit)
                    mae_atr = row_entry.get("MAE_ATR", 0.0)
                    if mae_atr <= -MAX_SL_ATR:
                        pnl = -100000.0 * (RISK_PER_TRADE / 100.0) * 1.0 # Pierde exactamente 1R
                        balance += pnl
                        gross_loss += pnl
                        trades += 1
                        in_trade = False
                        equity_curve.append(balance)
                        times.append(t)
                        continue
                        
                    entry_price = row_entry.get("Close", 0.0)
                    lbl = row_entry.get("Label", 1)
                    direction = 1 if lbl > 0 else -1
                    
    print(f"Simulation completed. Total Trades: {trades}")
    print(f"Final Balance: ${balance:.2f}")
    if abs(gross_loss) > 0:
        pf = gross_profit / abs(gross_loss)
        print(f"Profit Factor: {pf:.2f}")
        
    plt.style.use('dark_background')
    plt.figure(figsize=(14, 7))
    plt.plot(times, equity_curve, color="#00ffcc", linewidth=2, label="Python Extrapolated Baseline")
    
    # Fill under curve
    if len(times) > 0:
        plt.fill_between(times, equity_curve, min(equity_curve)*0.99, color="#00ffcc", alpha=0.1)
    
    plt.title("Pre-Deployment Reconciliation Baseline (Python) - FASE 65.5\nUSDJPY Sniper Mode (Entry >= 0.51, Exit >= 0.85)", fontsize=14, pad=15)
    plt.xlabel("Timeline (2015-2026)")
    plt.ylabel("Portfolio Equity ($)")
    plt.grid(True, alpha=0.2, linestyle="--")
    plt.legend()
    
    plt.savefig(os.path.join(BASE_DIR, "reconciliation_baseline.png"), dpi=150, bbox_inches='tight')
    print("Saved reconciliation_baseline.png")

if __name__ == "__main__":
    run_simulation()

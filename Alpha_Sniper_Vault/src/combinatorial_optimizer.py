import os
import json
import joblib
import pandas as pd
import numpy as np
import itertools
import argparse
from scipy.optimize import minimize
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--symbols', type=str, default="USDJPY,EURUSD,GBPUSD,XAUUSD,EURJPY")
args = parser.parse_known_args()[0]

BASE_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "models")
SYMBOLS = [s.strip() for s in args.symbols.split(",")]

# FASE 64 Sniper Mode Thresholds
ENTRY_THRESH = 0.51
RISK_PER_TRADE = 1.5
MAX_SL_ATR = 5.0

def get_expected_features(model, df_cols=None):
    if hasattr(model, "expected_features_"): return list(model.expected_features_)
    if hasattr(model, "feature_names_in_"): return list(model.feature_names_in_)
    
    n_feat = getattr(model, "n_features_in_", 0)
    if n_feat == 30:
        return [
            "Z_Score", "ATR_Norm", "Cross_Vol_Regime", "Fract_Diff_Return",
            "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", 
            "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour",
            "Session_Time", "H4_Trend_Align", "ATR_Ratio_High", "Energy_Accumulation",
            "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep", "Dist_Asian_High_ATR",
            "Dist_Asian_Low_ATR", "Is_Asian_Sweep", "Spread_Expansion_Ratio",
            "Candle_Dominance", "Regime_Consistency_Count",
            "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
            "TWAP_Z_Score", "Breakout_Velocity", "Day_Of_Week"
        ]
    
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

def extract_asset_returns(symbol):
    print(f"Extracting returns for {symbol}...")
    df_path = os.path.join(DATA_DIR, f"Struct_Dataset_{symbol}.csv")
    exit_path = os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{symbol}.csv")
    if not os.path.exists(df_path): return None
    
    df = pd.read_csv(df_path)
    df["Time"] = pd.to_datetime(df["Time"])
    
    uni_entry_path = os.path.join(OUT_DIR, f"modelo_universal_{symbol}_entry.pkl")
    files = [f for f in os.listdir(OUT_DIR) if f.startswith(f"modelo_universal_{symbol}_entry_")]
    if files: uni_entry_path = os.path.join(OUT_DIR, sorted(files)[-1])
    
    if not os.path.exists(uni_entry_path): return None
    uni_entry_model = joblib.load(uni_entry_path)
    
    exp_feats_entry = get_expected_features(uni_entry_model, df.columns)
    ignore_cols = ["Ticket", "Time", "Label", "Realized_RR", "Proba_Entry", "Proba_Exit", "Is_Asian_Sweep", "Toxic_Regime"]
    all_features_entry = [c for c in df.columns if c not in ignore_cols and df[c].dtype in ['float64', 'int64']]
    
    scaler_entry_path = os.path.join(OUT_DIR, f"scaler_universal_{symbol}_entry.pkl")
    if os.path.exists(scaler_entry_path):
        scaler = joblib.load(scaler_entry_path)
        s_feats = getattr(scaler, "feature_names_in_", all_features_entry)
        if hasattr(scaler, "n_features_in_") and len(s_feats) > scaler.n_features_in_: s_feats = s_feats[:scaler.n_features_in_]
        X_s = df[s_feats].fillna(0)
        X_scaled = scaler.transform(X_s)
        X_entry = pd.DataFrame(X_scaled, columns=s_feats)
        for c in exp_feats_entry:
            if c not in X_entry.columns: X_entry[c] = 0
        X_entry = X_entry[exp_feats_entry]
    else:
        X_entry = df[[c for c in exp_feats_entry if c in df.columns]].fillna(0)
        
    n_expected = getattr(uni_entry_model, "n_features_in_", len(X_entry.columns))
    if len(X_entry.columns) > n_expected: X_entry = X_entry.iloc[:, :n_expected]
    
    if len(X_entry.columns) == n_expected:
        probas = uni_entry_model.predict_proba(X_entry)
        if probas.shape[1] > 1:
            df["Proba_Entry"] = probas[:, 1].astype(float)
        else:
            df["Proba_Entry"] = 0.0
    else: return None

    df_exit = pd.DataFrame()
    if os.path.exists(exit_path):
        df_exit = pd.read_csv(exit_path)
        uni_exit_path = os.path.join(OUT_DIR, f"modelo_universal_{symbol}_exit.pkl")
        files = [f for f in os.listdir(OUT_DIR) if f.startswith(f"modelo_universal_{symbol}_exit_")]
        if files: uni_exit_path = os.path.join(OUT_DIR, sorted(files)[-1])
        if os.path.exists(uni_exit_path):
            uni_exit_model = joblib.load(uni_exit_path)
            exp_feats_exit = get_expected_features(uni_exit_model, df_exit.columns)
            all_features_exit = [c for c in df_exit.columns if c not in ignore_cols and df_exit[c].dtype in ['float64', 'int64']]
            scaler_exit_path = os.path.join(OUT_DIR, f"scaler_universal_{symbol}_exit.pkl")
            if os.path.exists(scaler_exit_path):
                scaler = joblib.load(scaler_exit_path)
                s_feats = getattr(scaler, "feature_names_in_", all_features_exit)
                if hasattr(scaler, "n_features_in_") and len(s_feats) > scaler.n_features_in_: s_feats = s_feats[:scaler.n_features_in_]
                X_s = df_exit[s_feats].fillna(0)
                X_scaled = scaler.transform(X_s)
                X_exit = pd.DataFrame(X_scaled, columns=s_feats)
                for c in exp_feats_exit:
                    if c not in X_exit.columns: X_exit[c] = 0
                X_exit = X_exit[exp_feats_exit]
            else:
                X_exit = df_exit[[c for c in exp_feats_exit if c in df_exit.columns]].fillna(0)
                
            n_expected_exit = getattr(uni_exit_model, "n_features_in_", len(X_exit.columns))
            if len(X_exit.columns) > n_expected_exit: X_exit = X_exit.iloc[:, :n_expected_exit]
            if len(X_exit.columns) == n_expected_exit:
                probas_exit = uni_exit_model.predict_proba(X_exit)
                if probas_exit.shape[1] > 1:
                    df_exit["Proba_Exit"] = probas_exit[:, 1].astype(float)
                else:
                    df_exit["Proba_Exit"] = 0.0
            else: df_exit["Proba_Exit"] = 0.0
            
    entries = df[(df["Proba_Entry"] >= ENTRY_THRESH)].copy()
    if "SL_Dist_ATR" in entries.columns: entries = entries[entries["SL_Dist_ATR"] <= MAX_SL_ATR]
    
    all_trades = []
    for _, row in entries.iterrows():
        t = row["Ticket"]
        rr = row.get("Realized_RR", -1.0)
        if not df_exit.empty and "Ticket" in df_exit.columns:
            pexit = df_exit[df_exit["Ticket"] == t]
            exit_signals = pexit[pexit["Proba_Exit"] >= 0.85]
            if not exit_signals.empty:
                rr = exit_signals.iloc[0].get("Open_Profit_R", rr)
                
        if pd.isna(rr): rr = -1.0
        if "MAE_ATR" in row and row["MAE_ATR"] <= -MAX_SL_ATR: rr = -1.0
        
        all_trades.append({"Date": row["Time"].date(), "Return_Pct": (rr * RISK_PER_TRADE) / 100.0})
        
    if not all_trades: return None
    df_trades = pd.DataFrame(all_trades)
    daily = df_trades.groupby("Date")["Return_Pct"].sum().reset_index()
    daily = daily.set_index("Date").sort_index()
    daily.columns = [symbol]
    return daily

def calc_max_drawdown(equity_curve):
    peak = equity_curve.expanding(min_periods=1).max()
    drawdown = (equity_curve - peak) / peak
    return drawdown.min()

def montecarlo_permutation(returns, iterations=2000):
    real_sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-9)
    ret_arr = returns.values.copy()
    count_beat = 0
    for _ in range(iterations):
        np.random.shuffle(ret_arr)
        # Random sign flip to represent random walk with same volatility
        random_signs = np.random.choice([-1, 1], size=len(ret_arr))
        sim_ret = ret_arr * random_signs
        sim_sharpe = np.sqrt(252) * sim_ret.mean() / (sim_ret.std() + 1e-9)
        if sim_sharpe >= real_sharpe:
            count_beat += 1
    p_value = count_beat / iterations
    return p_value

def calculate_inverse_volatility_weights(returns_df):
    vols = returns_df.std()
    inv_vols = 1.0 / (vols + 1e-9)
    weights = inv_vols / inv_vols.sum()
    return weights

def run_optimizer():
    returns_list = []
    valid_symbols = []
    for sym in SYMBOLS:
        ret = extract_asset_returns(sym)
        if ret is not None and len(ret) > 0:
            returns_list.append(ret)
            valid_symbols.append(sym)
            
    if not returns_list:
        print("No valid asset returns found.")
        return
        
    # Merge all into one dataframe, filling NaN with 0 (days where an asset didn't trade)
    df_all = pd.concat(returns_list, axis=1).fillna(0)
    
    results = []
    
    # Generate combinations from 1 to N
    for r in range(1, len(valid_symbols) + 1):
        for combo in itertools.combinations(valid_symbols, r):
            df_combo = df_all[list(combo)]
            
            # Check Max 30-Day Rolling Correlation if more than 1 asset
            max_corr = 0
            if r > 1:
                # Calculate 30-day rolling correlation between all pairs
                for i in range(len(combo)):
                    for j in range(i+1, len(combo)):
                        roll_corr = df_combo[combo[i]].rolling(30).corr(df_combo[combo[j]]).fillna(0)
                        max_pair_corr = roll_corr.max()
                        if max_pair_corr > max_corr: max_corr = max_pair_corr
                        
            # If max_corr > 0.6, discard!
            if max_corr > 0.6:
                continue
                
            # Asset Allocation: Inverse Volatility Weighting
            weights = calculate_inverse_volatility_weights(df_combo)
            
            # Aggregate portfolio returns
            port_ret = (df_combo * weights).sum(axis=1)
            
            # Calculate Metrics
            mean_ret = port_ret.mean() * 252
            std_ret = port_ret.std() * np.sqrt(252)
            sharpe = mean_ret / (std_ret + 1e-9)
            
            equity = (1 + port_ret).cumprod()
            max_dd = calc_max_drawdown(equity)
            
            # Golden Rule Filters
            if sharpe >= 1.4 and abs(max_dd) <= 0.15:
                results.append({
                    "Combo": combo,
                    "Weights": weights.to_dict(),
                    "Sharpe": sharpe,
                    "Drawdown": abs(max_dd),
                    "Max_Corr": max_corr,
                    "Port_Returns": port_ret
                })
                
    if not results:
        print("No portfolio combination passed the Golden Rules (Sharpe >= 1.4, DD <= 15%, Corr <= 0.6)")
        return
        
    # Rank by Sharpe
    results = sorted(results, key=lambda x: x["Sharpe"], reverse=True)
    best = results[0]
    
    print("\n" + "="*50)
    print("FASE 65: COMBINATORIAL ALIGNMENT FOUND")
    print("="*50)
    print(f"Winning Assets: {', '.join(best['Combo'])}")
    print(f"Sharpe Ratio: {best['Sharpe']:.2f}")
    print(f"Max Drawdown: {best['Drawdown']*100:.2f}%")
    print(f"Max 30D Rolling Correlation: {best['Max_Corr']:.2f}")
    
    print("\nRecommended Asset Allocation (Inverse Volatility):")
    for k, v in best["Weights"].items():
        print(f"  - {k}: {v*100:.1f}%")
        
    print("\nRunning Monte Carlo Anti-Overfitting Test (2000 iterations)...")
    p_val = montecarlo_permutation(best["Port_Returns"], 2000)
    print(f"P-Value: {p_val:.4f}")
    if p_val < 0.01:
        print("STATISTICALLY SIGNIFICANT. Alpha confirmed.")
    else:
        print("WARNING: High P-Value. Risk of overfitting.")

    # Save details for the walkthrough
    with open(os.path.join(BASE_DIR, "combinatorial_results.json"), "w") as f:
        # Convert series to list for json serialization
        res_json = {
            "combo": best["Combo"],
            "sharpe": best["Sharpe"],
            "dd": best["Drawdown"],
            "corr": best["Max_Corr"],
            "weights": best["Weights"],
            "p_value": p_val
        }
        json.dump(res_json, f, indent=4)

if __name__ == "__main__":
    run_optimizer()

import pandas as pd
import numpy as np
import joblib
import json
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "models")

LEAKAGE_COLS = ["Ticket", "Time", "Label", "Realized_RR", "_kfold", "_weight"]
EXIT_LEAKAGE_COLS = ["Ticket", "Time", "Bars_In_Trade", "Open_Profit_R", "Label", "_kfold", "_weight"]

SYMBOLS = ["USDJPY", "GBPUSD", "EURUSD", "EURJPY", "XAUUSD", "XAGUSD"]

ENTRY_FEATURES = [
    "Z_Score", "ATR_Norm", "RSI", "RSI_Extreme", "Bars_Since_Ext",
    "HMA_Slope_Pct", "HMA_Accel", "Breakout_Force_ATR",
    "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", "Pullback_Dur", "Pullback_Depth_Pct",
    "SL_Dist_ATR", "Hour",
    "Session_Time", "H4_Trend_Align", "Vol_Spread_Ratio",
    "ATR_Ratio_High", "RSI_Slope_10", "Spread_Impact_Ratio",
    "HMA_Velocity", "HMA_Acceleration", "HMA_Jerk", "Energy_Accumulation",
    "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep", "Bars_Since_Vol_Shock",
    "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR", "Is_Asian_Sweep",
    "Tick_Volume_ZScore", "Spread_Expansion_Ratio", "Candle_Dominance",
    "Regime_Consistency_Count", "RSI_Exhausted",
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev"
]

EXIT_FEATURES = [
    "Bars_In_Trade", "Open_Profit_R", "Drawdown_From_Peak_R", "Macro_ADX_Exit", 
    "Exit_HMA_Velocity", "Exit_HMA_Accel", "Exit_RSI", "Exit_Volatility_Ratio",   
    "Is_Trigger_Fast", "Is_Trigger_Slow", "Is_Trigger_RSI", "Is_Trigger_Profit",       
    "Is_Trigger_Fast_HMA_Cross", "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
    "Peak_HMA_Stretch_ATR", "Current_HMA_Stretch_ATR", "Elastic_Retracement_Pct"
]

def load_data(symbol):
    entry_csv = os.path.join(DATA_DIR, f"Struct_Dataset_{symbol}.csv")
    exit_csv = os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{symbol}.csv")
    if not os.path.exists(entry_csv) or not os.path.exists(exit_csv):
        return None, None
    return pd.read_csv(entry_csv), pd.read_csv(exit_csv)

def get_latest_suffix(symbol):
    json_files = glob.glob(os.path.join(OUT_DIR, f"umbrales_universales_{symbol}_*.json"))
    if not json_files: return None
    json_files.sort()
    base_name = os.path.basename(json_files[-1])
    prefix = f"umbrales_universales_{symbol}"
    return base_name[len(prefix):-5]

all_trades = []

for symbol in SYMBOLS:
    suffix = get_latest_suffix(symbol)
    if not suffix: continue
    
    with open(os.path.join(OUT_DIR, f"umbrales_universales_{symbol}{suffix}.json"), "r") as f:
        data = json.load(f)
        profile = data.get("B_Balanceado", list(data.values())[0])
        entry_thresh, exit_thresh = profile["entry_thresh"], profile["exit_thresh"]
        
    df_entry, df_exit = load_data(symbol)
    if df_entry is None: continue
    
    # Regime
    scaler = joblib.load(os.path.join(OUT_DIR, f"scaler_universal_{symbol}_regimen{suffix}.pkl"))
    kmeans = joblib.load(os.path.join(OUT_DIR, f"regimen_universal_{symbol}_kmeans{suffix}.pkl"))
    with open(os.path.join(OUT_DIR, f"toxic_universal_{symbol}{suffix}.json"), "r") as f:
        toxic_id = json.load(f)["toxic_id"]
        
    df_entry_clean = df_entry.copy()
    if 'Label' in df_entry_clean.columns: df_entry_clean = df_entry_clean[df_entry_clean['Label'] != -1].copy()
    
    regime_feats = ["ATR_Norm", "Bollinger_Dev", "Z_Score", "MTF_ATR_Ratio", "Macro_ADX"]
    regime_feats = [c for c in regime_feats if c in df_entry_clean.columns]
    if len(regime_feats) > 0:
        df_entry_clean["_cluster"] = kmeans.predict(scaler.transform(df_entry_clean[regime_feats].fillna(0)))
        df_entry_clean = df_entry_clean[df_entry_clean["_cluster"] != toxic_id].copy()
    
    # Entry
    entry_model = joblib.load(os.path.join(OUT_DIR, f"modelo_universal_{symbol}_entry{suffix}.pkl"))
    for c in ENTRY_FEATURES:
        if c not in df_entry_clean.columns: df_entry_clean[c] = 0.0
    probs = entry_model.predict_proba(df_entry_clean[ENTRY_FEATURES].values)[:, 1]
    
    proba_map = dict(zip(df_entry_clean["Ticket"], probs))
    df_entry["entry_proba"] = df_entry["Ticket"].map(proba_map).fillna(0.0)
    
    # Exit
    exit_model = joblib.load(os.path.join(OUT_DIR, f"modelo_universal_{symbol}_exit{suffix}.pkl"))
    for c in EXIT_FEATURES:
        if c not in df_exit.columns: df_exit[c] = 0.0
    df_exit["exit_proba"] = exit_model.predict_proba(df_exit[EXIT_FEATURES].values)[:, 1]
    
    # Fusion
    df_ex = df_exit[["Ticket", "Bars_In_Trade", "Open_Profit_R", "exit_proba"]].sort_values(["Ticket", "Bars_In_Trade"])
    grp = df_ex.groupby("Ticket")
    exit_map = { t: { "bars": g["Bars_In_Trade"].values, "float_rr": g["Open_Profit_R"].values, "exit_proba": g["exit_proba"].values } for t, g in grp }
    
    df_selected = df_entry[df_entry["entry_proba"] >= entry_thresh].copy()
    
    def get_effective_rr(row):
        t = row["Ticket"]
        brr = float(row["Realized_RR"])
        err = brr
        if t in exit_map:
            em = exit_map[t]
            mask = em["exit_proba"] >= exit_thresh
            if mask.any(): err = float(em["float_rr"][np.argmax(mask)])
        
        hit_so = (err >= 1.5 or brr >= 1.5)
        if t in exit_map and not hit_so and (em["float_rr"] >= 1.5).any(): hit_so = True
        return (1.5 * 0.5) + (max(err, 0.0) * 0.5) if hit_so else err

    if len(df_selected) > 0:
        df_selected["effective_rr"] = df_selected.apply(get_effective_rr, axis=1)
        df_selected["Symbol"] = symbol
        all_trades.append(df_selected[["Time", "Symbol", "effective_rr"]])

if all_trades:
    df_all = pd.concat(all_trades, ignore_index=True)
    df_all["Time"] = pd.to_datetime(df_all["Time"])
    df_all = df_all.sort_values("Time").reset_index(drop=True)
    
    # Filter up to 2023 inclusive as requested by user
    df_all = df_all[df_all["Time"].dt.year <= 2023].copy()
    
    # Compounding sequentially
    df_all["Return"] = df_all["effective_rr"] * 0.01
    df_all["Equity"] = np.cumprod(1 + df_all["Return"]) * 10000 # Assume $10k start
    
    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(df_all["Time"], df_all["Equity"], color="#00ffcc", linewidth=1.5, label="Master 8 (B_Balanceado)")
    ax.fill_between(df_all["Time"], df_all["Equity"], 10000, where=(df_all["Equity"] >= 10000), interpolate=True, color="#00ffcc", alpha=0.1)
    
    ax.set_title("Alpha Sniper: Expected Portfolio Equity Curve (2015-2023)\nRisk: 1% per trade", fontsize=16, fontweight="bold", color="white")
    ax.set_xlabel("Time", fontsize=12, color="lightgray")
    ax.set_ylabel("Account Balance ($)", fontsize=12, color="lightgray")
    
    ax.tick_params(colors='lightgray')
    ax.grid(color='#333333', linestyle='--', linewidth=0.5)
    
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    plt.legend(facecolor='#1e1e1e', edgecolor='lightgray', labelcolor='white')
    plt.tight_layout()
    
    plot_path = os.path.join(OUT_DIR, "portfolio_expected_equity_2023.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"Equity curve saved to {plot_path}")

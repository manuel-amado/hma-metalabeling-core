import pandas as pd
import numpy as np
import joblib
import json
import glob
import os
import re

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
    df_entry = pd.read_csv(entry_csv)
    df_exit = pd.read_csv(exit_csv)
    return df_entry, df_exit

def get_latest_suffix(symbol):
    json_files = glob.glob(os.path.join(OUT_DIR, f"umbrales_universales_{symbol}_*.json"))
    if not json_files: return None
    json_files.sort()
    latest = json_files[-1]
    base_name = os.path.basename(latest)
    prefix = f"umbrales_universales_{symbol}"
    return base_name[len(prefix):-5]

all_yearly_results = []

for symbol in SYMBOLS:
    suffix = get_latest_suffix(symbol)
    if not suffix:
        print(f"Skipping {symbol}, no models found.")
        continue
    
    # Load config
    with open(os.path.join(OUT_DIR, f"umbrales_universales_{symbol}{suffix}.json"), "r") as f:
        data = json.load(f)
        profile = data.get("B_Balanceado", list(data.values())[0])
        entry_thresh = profile["entry_thresh"]
        exit_thresh = profile["exit_thresh"]
        
    df_entry, df_exit = load_data(symbol)
    if df_entry is None: continue
    
    print(f"Procesando {symbol} (Thresholds: IN={entry_thresh}, OUT={exit_thresh})")
    
    # Regime
    scaler = joblib.load(os.path.join(OUT_DIR, f"scaler_universal_{symbol}_regimen{suffix}.pkl"))
    kmeans = joblib.load(os.path.join(OUT_DIR, f"regimen_universal_{symbol}_kmeans{suffix}.pkl"))
    with open(os.path.join(OUT_DIR, f"toxic_universal_{symbol}{suffix}.json"), "r") as f:
        toxic_id = json.load(f)["toxic_id"]
        
    df_entry_clean = df_entry.copy()
    if 'Label' in df_entry_clean.columns:
        df_entry_clean = df_entry_clean[df_entry_clean['Label'] != -1].copy()
        
    regime_feats = ["ATR_Norm", "Bollinger_Dev", "Z_Score", "MTF_ATR_Ratio", "Macro_ADX"]
    regime_feats = [c for c in regime_feats if c in df_entry_clean.columns]
    
    if len(regime_feats) > 0:
        X_regime = df_entry_clean[regime_feats].fillna(0)
        X_scaled = scaler.transform(X_regime)
        clusters = kmeans.predict(X_scaled)
        df_entry_clean["_cluster"] = clusters
        
        valid_mask = (df_entry_clean["_cluster"] != toxic_id)
        df_entry_clean = df_entry_clean[valid_mask].copy()
    
    # Entry
    entry_model = joblib.load(os.path.join(OUT_DIR, f"modelo_universal_{symbol}_entry{suffix}.pkl"))
    for c in ENTRY_FEATURES:
        if c not in df_entry_clean.columns:
            df_entry_clean[c] = 0.0
    X_entry = df_entry_clean[ENTRY_FEATURES].values
    
    probs = entry_model.predict_proba(X_entry)[:, 1]
    
    # Map back
    proba_map = dict(zip(df_entry_clean["Ticket"], probs))
    df_entry["entry_proba"] = df_entry["Ticket"].map(proba_map)
    df_entry["entry_proba"] = df_entry["entry_proba"].fillna(0.0)
    
    # Exit
    exit_model = joblib.load(os.path.join(OUT_DIR, f"modelo_universal_{symbol}_exit{suffix}.pkl"))
    for c in EXIT_FEATURES:
        if c not in df_exit.columns:
            df_exit[c] = 0.0
    X_exit = df_exit[EXIT_FEATURES].values
    df_exit["exit_proba"] = exit_model.predict_proba(X_exit)[:, 1]
    
    # Fusion
    exit_cols_needed = ["Ticket", "Bars_In_Trade", "Open_Profit_R", "exit_proba"]
    df_ex = df_exit[exit_cols_needed].sort_values(["Ticket", "Bars_In_Trade"])
    grp = df_ex.groupby("Ticket")
    exit_map = {
        ticket: {
            "bars":       grp_df["Bars_In_Trade"].values,
            "float_rr":   grp_df["Open_Profit_R"].values,
            "exit_proba": grp_df["exit_proba"].values,
        }
        for ticket, grp_df in grp
    }
    
    # Simulation
    df_selected = df_entry[df_entry["entry_proba"] >= entry_thresh].copy()
    if len(df_selected) == 0:
        continue
        
    def get_effective_rr(row):
        ticket = row["Ticket"]
        base_rr = float(row["Realized_RR"])
        exit_model_rr = base_rr
        if ticket in exit_map:
            em = exit_map[ticket]
            mask = em["exit_proba"] >= exit_thresh
            if mask.any():
                first_idx = np.argmax(mask)
                exit_model_rr = float(em["float_rr"][first_idx])
        
        hit_scale_out = False
        if exit_model_rr >= 1.5 or base_rr >= 1.5:
            hit_scale_out = True
        elif ticket in exit_map:
            if (em["float_rr"] >= 1.5).any():
                hit_scale_out = True
                
        if hit_scale_out:
            rr_mitad_2 = exit_model_rr if exit_model_rr >= 0 else 0.0
            return (1.5 * 0.5) + (rr_mitad_2 * 0.5)
        else:
            return exit_model_rr

    df_selected["effective_rr"] = df_selected.apply(get_effective_rr, axis=1)
    df_selected["Time"] = pd.to_datetime(df_selected["Time"])
    df_selected["Year"] = df_selected["Time"].dt.year
    
    years = df_selected["Year"].unique()
    years.sort()
    
    for y in years:
        df_y = df_selected[df_selected["Year"] == y]
        rr_series = df_y["effective_rr"].values.astype(float)
        equity_pct = rr_series * 0.01
        
        if len(equity_pct) == 0:
            continue
            
        equity_curve = np.cumprod(1 + equity_pct)
        total_return = (equity_curve[-1] - 1.0) * 100
        
        mean_r = np.mean(equity_pct)
        std_r = np.std(equity_pct, ddof=1)
        sharpe = 0.0 if std_r < 1e-9 else (mean_r / std_r) * np.sqrt(252)
        
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        max_dd = abs(drawdown.min()) * 100.0
        
        win_rate = (rr_series > 0).mean() * 100
        
        all_yearly_results.append({
            "Symbol": symbol,
            "Year": int(y),
            "Return": total_return,
            "MaxDD": max_dd,
            "Sharpe": sharpe,
            "WinRate": win_rate,
            "Trades": len(rr_series)
        })

df_res = pd.DataFrame(all_yearly_results)
df_res.to_csv(os.path.join(OUT_DIR, "yearly_report_raw.csv"), index=False)

# Generate Markdown
md = "# Radiografía Anual de Rendimientos y Métricas (Macro 6)\n\n"
md += "Operando cada activo individual con **Riesgo Fijo del 1% por trade** (Perfil B_Balanceado).\n\n"

# 1. Pivot Table Return
pivot_ret = df_res.pivot(index="Year", columns="Symbol", values="Return").fillna(0.0)
pivot_ret["Total_Portfolio"] = pivot_ret.sum(axis=1)

md += "## 📊 Rentabilidad Anual (Return %)\n\n"
md += "| Año | " + " | ".join(pivot_ret.columns) + " |\n"
md += "| :---: | " + " | ".join(["---:"] * len(pivot_ret.columns)) + " |\n"
for year, row in pivot_ret.iterrows():
    vals = [f"**{row['Total_Portfolio']:.2f}%**" if c == "Total_Portfolio" else f"{row[c]:.2f}%" for c in pivot_ret.columns]
    md += f"| **{int(year)}** | " + " | ".join(vals) + " |\n"

# 2. Pivot Table Max Drawdown
pivot_dd = df_res.pivot(index="Year", columns="Symbol", values="MaxDD").fillna(0.0)
md += "\n## 📉 Maximum Drawdown Anual (%)\n\n"
md += "| Año | " + " | ".join(pivot_dd.columns) + " |\n"
md += "| :---: | " + " | ".join(["---:"] * len(pivot_dd.columns)) + " |\n"
for year, row in pivot_dd.iterrows():
    vals = [f"{row[c]:.2f}%" for c in pivot_dd.columns]
    md += f"| **{int(year)}** | " + " | ".join(vals) + " |\n"

# 3. Pivot Table Win Rate
pivot_wr = df_res.pivot(index="Year", columns="Symbol", values="WinRate").fillna(0.0)
md += "\n## 🎯 Win Rate Anual (%)\n\n"
md += "| Año | " + " | ".join(pivot_wr.columns) + " |\n"
md += "| :---: | " + " | ".join(["---:"] * len(pivot_wr.columns)) + " |\n"
for year, row in pivot_wr.iterrows():
    vals = [f"{row[c]:.2f}%" for c in pivot_wr.columns]
    md += f"| **{int(year)}** | " + " | ".join(vals) + " |\n"
    
# 4. Pivot Table Trades
pivot_tr = df_res.pivot(index="Year", columns="Symbol", values="Trades").fillna(0)
md += "\n## 🔄 Operaciones (Trades) Anuales\n\n"
md += "| Año | " + " | ".join(pivot_tr.columns) + " | Total |\n"
md += "| :---: | " + " | ".join(["---:"] * (len(pivot_tr.columns) + 1)) + " |\n"
for year, row in pivot_tr.iterrows():
    vals = [f"{int(row[c])}" for c in pivot_tr.columns]
    total = int(row.sum())
    md += f"| **{int(year)}** | " + " | ".join(vals) + f" | **{total}** |\n"

out_md = os.path.join(BASE_DIR, "portfolio_yearly_breakdown_2026.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nReporte guardado en: {out_md}")

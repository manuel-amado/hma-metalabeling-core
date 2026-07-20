import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Python_ML"
OUT_DIR = os.path.join(BASE_DIR, "output")
LOG_PATH = os.path.join(OUT_DIR, "portfolio_trades_log.csv")

try:
    from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES
except:
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
        "Regime_Consistency_Count", "RSI_Exhausted"
    ]
    EXIT_FEATURES = [
        "Bars_In_Trade", "Open_Profit_R", "Drawdown_From_Peak_R", "Macro_ADX_Exit",
        "Exit_HMA_Velocity", "Exit_HMA_Accel", "Exit_RSI", "Exit_Volatility_Ratio",
        "Spread_Impact_Exit", "Is_Trigger_Fast", "Is_Trigger_Slow",
        "Is_Trigger_RSI", "Is_Trigger_Profit", "Is_Trigger_Fast_HMA_Cross"
    ]

import glob
json_files = glob.glob(os.path.join(OUT_DIR, "production_thresholds_*.json"))
activos_upper = [os.path.basename(f).replace("production_thresholds_", "").replace(".json", "") for f in json_files]
activos = activos_upper

def analyze_features():
    output = "## Importancia de Características (Feature Importance) por Activo\n\n"
    for activo_u, activo in zip(activos_upper, activos):
        output += f"### {activo_u}\n"
        # Entry Model
        entry_path = os.path.join(OUT_DIR, f"entry_model_{activo}.pkl")
        if os.path.exists(entry_path):
            try:
                model = joblib.load(entry_path)
                importances = model.feature_importances_
                indices = np.argsort(importances)[::-1][:5]
                output += "- **Top 5 Entry Features:**\n"
                for i in indices:
                    output += f"  - `{ENTRY_FEATURES[i]}`: {importances[i]*100:.2f}%\n"
            except Exception as e:
                pass
                
        # Exit Model
        exit_path = os.path.join(OUT_DIR, f"exit_model_{activo}.pkl")
        if os.path.exists(exit_path):
            try:
                model = joblib.load(exit_path)
                importances = model.feature_importances_
                indices = np.argsort(importances)[::-1][:3]
                output += "- **Top 3 Exit Features:**\n"
                for i in indices:
                    output += f"  - `{EXIT_FEATURES[i]}`: {importances[i]*100:.2f}%\n"
            except Exception as e:
                pass
        output += "\n"
    return output

def run_audit():
    if not os.path.exists(LOG_PATH):
        return "El archivo portfolio_trades_log.csv no existe todavía."
        
    df = pd.read_csv(LOG_PATH)
    
    output = "# Auditoría Global del Portafolio Alpha Sniper\n\n"
    output += "## Métricas de Rendimiento Desglosadas por Divisa\n\n"
    output += "| Activo | Trades | Win Rate | Profit Factor | Beneficio Neto (USD) | MFE Promedio (R) |\n"
    output += "|---|---|---|---|---|---|\n"
    
    total_profit = 0
    for activo_u, activo in zip(activos_upper, activos):
        df_a = df[df['Symbol'] == activo]
        if df_a.empty:
            output += f"| {activo_u} | 0 | - | - | $0 | - |\n"
            continue
            
        trades = len(df_a)
        wins = len(df_a[df_a['Profit_USD'] > 0])
        win_rate = (wins / trades) * 100
        
        gross_profit = df_a[df_a['Profit_USD'] > 0]['Profit_USD'].sum()
        gross_loss = abs(df_a[df_a['Profit_USD'] <= 0]['Profit_USD'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        net_profit = df_a['Profit_USD'].sum()
        total_profit += net_profit
        
        # MFE Promedio
        mfe_promedio = df_a['MFE_R'].mean() if 'MFE_R' in df_a.columns else 0.0
        
        output += f"| **{activo_u}** | {trades} | {win_rate:.1f}% | {profit_factor:.2f} | **${net_profit:,.2f}** | +{mfe_promedio:.2f}R |\n"
        
    output += f"\n**BENEFICIO TOTAL DEL PORTAFOLIO:** ${total_profit:,.2f}\n\n"
    
    # Activos Rechazados
    rechazados_path = os.path.join(OUT_DIR, "rejected_assets.json")
    if os.path.exists(rechazados_path):
        import json
        with open(rechazados_path, "r") as rf:
            rechazados = json.load(rf)
        if rechazados:
            output += "## 🚫 Activos Rechazados (Alpha Tóxico)\n\n"
            output += "Los siguientes activos demostraron un comportamiento errático, Alpha Score deficiente o incapacidad para ser modelados. Han sido eliminados del portfolio:\n"
            for r in rechazados:
                output += f"- **{r.upper()}**\n"
            output += "\n"
    
    output += analyze_features()
    
    with open(os.path.join(BASE_DIR, "auditoria_portfolio.md"), "w", encoding="utf-8") as f:
        f.write(output)
    
    return "Auditoría completada. Guardado en auditoria_portfolio.md"

if __name__ == "__main__":
    print(run_audit())

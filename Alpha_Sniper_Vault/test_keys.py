import sys
sys.path.append(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src')
from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES

# Simulate MQL5 JSON keys
mql5_keys = ["activo", "Z_Score", "ATR_Norm", "RSI", "RSI_Extreme", "Bars_Since_Ext", "HMA_Slope_Pct", "HMA_Accel", "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour", "Session_Time", "H4_Trend_Align", "Vol_Spread_Ratio", "ATR_Ratio_High", "RSI_Slope_10", "HMA_Velocity", "HMA_Acceleration", "HMA_Jerk", "Energy_Accumulation", "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep", "Bars_Since_Vol_Shock", "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR", "Is_Asian_Sweep", "Candle_Dominance", "Regime_Consistency_Count", "RSI_Exhausted", "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev"]

print("Missing ENTRY_FEATURES in MQL5 JSON:")
for f in ENTRY_FEATURES:
    if f not in mql5_keys:
        print(f" - {f}")


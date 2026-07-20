import sys
import json
import requests

payload = {
    "activo": "usdjpy",
    "features": {
        "Z_Score": 1.5,
        "ATR_Norm": 1.2,
        "RSI": 60.5,
        "RSI_Extreme": 0.0,
        "Bars_Since_Ext": 10.0,
        "HMA_Slope_Pct": 0.5,
        "HMA_Accel": 0.1,
        "Breakout_Force_ATR": 2.0,
        "Trend_Align": 1.0,
        "Dist_Macro_EMA": 1.5,
        "Macro_ADX": 35.0,
        "Pullback_Dur": 5.0,
        "Pullback_Depth_Pct": 0.3,
        "SL_Dist_ATR": 1.5,
        "Hour": 14.0,
        "Session_Time": 2.0,
        "H4_Trend_Align": 1.0,
        "Vol_Spread_Ratio": 1.5,
        "ATR_Ratio_High": 1.2,
        "RSI_Slope_10": 5.0,
        "HMA_Velocity": 0.2,
        "HMA_Acceleration": 0.05,
        "HMA_Jerk": -0.01,
        "Energy_Accumulation": 5.0,
        "Bars_Since_Asian_Sweep": 20.0,
        "Bars_Since_Local_Sweep": 15.0,
        "Bars_Since_Vol_Shock": 30.0,
        "Dist_Asian_High_ATR": 2.0,
        "Dist_Asian_Low_ATR": 4.0,
        "Is_Asian_Sweep": 0.0,
        "Candle_Dominance": 0.8,
        "Regime_Consistency_Count": 3.0,
        "RSI_Exhausted": 0.0,
        "MTF_ATR_Ratio": 1.1,
        "Trigger_Rejection_Tail": 0.1,
        "Bollinger_Dev": 1.8
    }
}

try:
    res = requests.post("http://127.0.0.1:8000/predict_entry", json=payload)
    print("ENTRY RESPONSE:", res.json())
except Exception as e:
    print("ERROR:", e)


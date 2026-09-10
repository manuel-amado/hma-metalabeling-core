import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize(): quit()

def analyze_friction(symbol, timeframe_name, timeframe_val):
    rates = mt5.copy_rates_from_pos(symbol, timeframe_val, 0, 50000)
    if rates is None: return None
    df = pd.DataFrame(rates)
    df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
    avg_atr = df['tr'].rolling(14).mean().mean()
    point = mt5.symbol_info(symbol).point
    avg_spread = (df['spread'] * point).mean()
    comm_points = 0.03 if symbol == 'XAUUSD' else 30.0
    total_friction = avg_spread + comm_points
    friction_pct_of_risk = (total_friction / (2 * avg_atr)) * 100
    return {
        'Symbol': symbol, 'TF': timeframe_name, 'Avg ATR': round(avg_atr,2),
        'Spread': round(avg_spread,2), 'Comm': round(comm_points,2),
        'Total Fric': round(total_friction,2), 'Fric % Risk': round(friction_pct_of_risk,2)
    }

results = []
for sym in ['XAUUSD', 'BTCUSD']:
    for tf_name, tf_val in [('M15', mt5.TIMEFRAME_M15), ('H1', mt5.TIMEFRAME_H1), ('H4', mt5.TIMEFRAME_H4)]:
        res = analyze_friction(sym, tf_name, tf_val)
        if res: results.append(res)
mt5.shutdown()

res_df = pd.DataFrame(results)
report = "# 📊 Análisis de Fricción Institucional\n\n"
report += res_df.to_markdown(index=False)
with open(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\friction_analysis.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("Friction analysis done.")
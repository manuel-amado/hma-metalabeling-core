import pandas as pd
import numpy as np
import MetaTrader5 as mt5

mt5.initialize()
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 10000)
df = pd.DataFrame(rates)
mt5.shutdown()

period = 1344
highs = df['high'].values
lows = df['low'].values
closes = df['close'].values

chops = []
for i in range(period, len(df)):
    sum_tr = 0.0
    max_h = -999999.0
    min_l = 999999.0
    for j in range(period):
        idx = i - period + j
        h = highs[idx]
        l = lows[idx]
        c_prev = closes[idx-1] if idx > 0 else closes[0]
        
        tr = max(h-l, abs(h-c_prev), abs(l-c_prev))
        sum_tr += tr
        
        if h > max_h: max_h = h
        if l < min_l: min_l = l
        
    range_hl = max_h - min_l
    if range_hl > 0:
        chop = 100.0 * np.log10(sum_tr / range_hl) / np.log10(period)
        chops.append(chop)

print(f"Mean CHOP: {np.mean(chops):.2f}")
print(f"Min CHOP: {np.min(chops):.2f}")
print(f"Max CHOP: {np.max(chops):.2f}")
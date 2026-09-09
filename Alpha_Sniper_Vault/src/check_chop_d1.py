import pandas as pd
import numpy as np
import MetaTrader5 as mt5

mt5.initialize()
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 100000)
mt5.shutdown()
if rates is None:
    print("No rates returned")
    quit()
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

df['date'] = df['time'].dt.date
daily_df = df.groupby('date').agg({'high': 'max', 'low': 'min', 'close': 'last'}).reset_index()

period = 14
highs = daily_df['high'].values
lows = daily_df['low'].values
closes = daily_df['close'].values

chops = []
for i in range(period, len(daily_df)):
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

print(f"Mean CHOP (D1 bars): {np.mean(chops):.2f}")
print(f"Min CHOP (D1 bars): {np.min(chops):.2f}")
print(f"Max CHOP (D1 bars): {np.max(chops):.2f}")
percent_above_61_8 = np.sum(np.array(chops) > 61.8) / len(chops) * 100
print(f"% Time above 61.8: {percent_above_61_8:.1f}%")
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize(): quit()
df_list = []
start = 0
while start < 300000:
    rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, start, 99000)
    if rates is None or len(rates) == 0:
        break
    df_list.append(pd.DataFrame(rates))
    start += 99000
mt5.shutdown()

df = pd.concat(df_list).drop_duplicates('time').sort_values('time')
df['time'] = pd.to_datetime(df['time'], unit='s')
print("Total bars:", len(df))
print("Start date:", df['time'].min())
print("End date:", df['time'].max())
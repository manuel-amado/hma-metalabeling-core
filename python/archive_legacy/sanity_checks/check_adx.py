import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import datetime

if not mt5.initialize(): quit()

utc_from = datetime.datetime(2015, 1, 1)
utc_to = datetime.datetime(2026, 12, 31)
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_D1, utc_from, utc_to)
mt5.shutdown()
df = pd.DataFrame(rates)

def rma(series, length):
    return series.ewm(alpha=1/length, adjust=False).mean()

df['up_move'] = df['high'] - df['high'].shift(1)
df['down_move'] = df['low'].shift(1) - df['low']
df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))

n = 14
df['atr'] = rma(df['tr'], n)
df['plus_di'] = 100 * rma(df['plus_dm'], n) / df['atr']
df['minus_di'] = 100 * rma(df['minus_dm'], n) / df['atr']
df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
df['adx'] = rma(df['dx'], n)

print("Mean ADX:", df['adx'].mean())
print("Min ADX:", df['adx'].min())
print("Max ADX:", df['adx'].max())
print("Percent < 25:", (df['adx'] < 25).mean() * 100)
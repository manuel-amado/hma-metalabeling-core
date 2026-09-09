import pandas as pd
import numpy as np

path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\USDJPY_M15_11Years.csv"
df = pd.read_csv(path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')
df.set_index('time', inplace=True)

m15_tr = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
print(f"USDJPY M15 Average ATR: {m15_tr.mean():.4f}")

df_h4 = df.resample('4h').agg({'open':'first', 'high':'max', 'low':'min', 'close':'last'}).dropna()
h4_tr = np.maximum(df_h4['high'] - df_h4['low'], np.maximum(abs(df_h4['high'] - df_h4['close'].shift(1)), abs(df_h4['low'] - df_h4['close'].shift(1))))
print(f"USDJPY H4 Average ATR: {h4_tr.mean():.4f}")
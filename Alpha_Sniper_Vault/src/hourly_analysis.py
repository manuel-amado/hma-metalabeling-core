import pandas as pd
import numpy as np

path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv"
df = pd.read_csv(path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')
df.set_index('time', inplace=True)

# Filter for the post-2022 regime
df = df[df.index >= '2022-01-01']

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma200'] = hma(df['close'], 200)
df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
df['rsi14'] = 100 - (100 / (1 + (gain/loss)))
df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()
df.dropna(inplace=True)

trades = []
in_trade = False
trade_dir = 0
entry_price = sl = risk_dist = 0.0
entry_hour = 0
entry_time = None

c = df['close'].values
h = df['high'].values
l = df['low'].values
hma_arr = df['hma200'].values
ema_arr = df['ema400'].values
rsi_arr = df['rsi14'].values
atr_arr = df['atr14'].values
hours = df.index.hour.values
times = df.index.values

for i in range(1, len(c)):
    if in_trade:
        if trade_dir == 1 and l[i] <= sl:
            trades.append({'hour': entry_hour, 'profit_r': -(entry_price - sl + 0.35) / risk_dist, 'time': entry_time})
            in_trade = False
        elif trade_dir == -1 and h[i] >= sl:
            trades.append({'hour': entry_hour, 'profit_r': -(sl - entry_price + 0.35) / risk_dist, 'time': entry_time})
            in_trade = False
        elif trade_dir == 1 and c[i] < hma_arr[i]:
            trades.append({'hour': entry_hour, 'profit_r': (c[i] - entry_price - 0.35) / risk_dist, 'time': entry_time})
            in_trade = False
        elif trade_dir == -1 and c[i] > hma_arr[i]:
            trades.append({'hour': entry_hour, 'profit_r': (entry_price - c[i] - 0.35) / risk_dist, 'time': entry_time})
            in_trade = False
    else:
        # Long
        if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < 70:
            in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = 1.5 * atr_arr[i]; sl = c[i] - risk_dist
            entry_hour = hours[i]; entry_time = times[i]
        # Short
        elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > 30:
            in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = 1.5 * atr_arr[i]; sl = c[i] + risk_dist
            entry_hour = hours[i]; entry_time = times[i]

tdf = pd.DataFrame(trades)
print("=== RENTABILIDAD POR HORA DE ENTRADA (Múltiplos de R) ===")
summary = tdf.groupby('hour').agg(
    Trades=('profit_r', 'count'),
    WinRate=('profit_r', lambda x: (x > 0).mean() * 100),
    Net_R=('profit_r', 'sum')
).round(2).sort_values('Net_R', ascending=False)
print(summary.to_string())

import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    wma_half = wma(s, int(period / 2))
    wma_full = wma(s, period)
    diff = (2 * wma_half) - wma_full
    return wma(diff, int(np.sqrt(period)))

if not mt5.initialize(): quit()

rates = mt5.copy_rates_from_pos("BTCUSD", mt5.TIMEFRAME_M15, 0, 99000)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
df['high_low'] = df['high'] - df['low']
df['high_close'] = np.abs(df['high'] - df['close'].shift())
df['low_close'] = np.abs(df['low'] - df['close'].shift())
df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
df['atr14'] = df['tr'].rolling(14).mean()

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi14'] = 100 - (100 / (1 + rs))

df['hma100'] = hma(df['close'], 100)
valid_df = df.dropna().copy().reset_index(drop=True)

trades = []
in_trade = False
trade_dir = 0
entry_price = 0.0
sl = 0.0

for i in range(1, len(valid_df)):
    if in_trade:
        if trade_dir == 1 and valid_df['low'].iloc[i] <= sl:
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'SL_BUY'})
            in_trade = False
        elif trade_dir == -1 and valid_df['high'].iloc[i] >= sl:
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'SL_SELL'})
            in_trade = False
        elif trade_dir == 1 and valid_df['close'].iloc[i] < valid_df['hma100'].iloc[i]:
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'EXIT_BUY'})
            in_trade = False
        elif trade_dir == -1 and valid_df['close'].iloc[i] > valid_df['hma100'].iloc[i]:
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'EXIT_SELL'})
            in_trade = False
    else:
        c = valid_df['close'].iloc[i]
        c_prev = valid_df['close'].iloc[i-1]
        h = valid_df['hma100'].iloc[i]
        h_prev = valid_df['hma100'].iloc[i-1]
        ema = valid_df['ema200'].iloc[i]
        rsi = valid_df['rsi14'].iloc[i]
        atr = valid_df['atr14'].iloc[i]
        
        if c_prev < h_prev and c > h and c > ema and rsi < 70:
            in_trade = True
            trade_dir = 1
            entry_price = c
            sl = c - 2 * atr
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'BUY', 'price': c, 'sl': sl})
        elif c_prev > h_prev and c < h and c < ema and rsi > 30:
            in_trade = True
            trade_dir = -1
            entry_price = c
            sl = c + 2 * atr
            trades.append({'time': valid_df['time'].iloc[i], 'type': 'SELL', 'price': c, 'sl': sl})

mt5.shutdown()
for t in trades[:10]:
    print(t)
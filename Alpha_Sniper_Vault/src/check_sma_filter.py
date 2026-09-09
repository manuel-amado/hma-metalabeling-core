import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

if not mt5.initialize(): quit()

utc_from = datetime.datetime(2021, 1, 1)
utc_to = datetime.datetime(2026, 1, 1)
# we can't fetch 2021-2026 M15 because of 50k limit. 
# We'll just fetch 50,000 bars (approx 2024-2025) and see if the filter cuts trades.
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 50000)
mt5.shutdown()
if rates is None: quit()

df = pd.DataFrame(rates)

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma100'] = hma(df['close'], 100)
df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
df['sma2000'] = df['close'].rolling(2000).mean()
df['sma2000_slope'] = abs(df['sma2000'] - df['sma2000'].shift(96)) # Change over 1 day

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi14'] = 100 - (100 / (1 + rs))

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()
df['atr2000'] = df['tr'].rolling(2000).mean()

vdf = df.dropna().copy()

def backtest(use_filter=False):
    r_multiples = []
    in_trade = False
    trade_dir = 0
    entry_price = 0
    risk_dist = 0
    sl = 0
    friction = 0.35
    
    for i in range(1, len(vdf)):
        if in_trade:
            if trade_dir == 1 and vdf['low'].iloc[i] <= sl:
                r_multiples.append(-(entry_price - sl + friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and vdf['high'].iloc[i] >= sl:
                r_multiples.append(-(sl - entry_price + friction) / risk_dist)
                in_trade = False
            elif trade_dir == 1 and vdf['close'].iloc[i] < vdf['hma100'].iloc[i]:
                r_multiples.append((vdf['close'].iloc[i] - entry_price - friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and vdf['close'].iloc[i] > vdf['hma100'].iloc[i]:
                r_multiples.append((entry_price - vdf['close'].iloc[i] - friction) / risk_dist)
                in_trade = False
        else:
            if use_filter:
                # If the 20-day SMA hasn't moved more than 2 * M15_ATR over the last day, it's ranging.
                if vdf['sma2000_slope'].iloc[i] < (vdf['atr14'].iloc[i] * 2.0):
                    continue
                    
            c = vdf['close'].iloc[i]
            c_p = vdf['close'].iloc[i-1]
            h = vdf['hma100'].iloc[i]
            h_p = vdf['hma100'].iloc[i-1]
            e = vdf['ema200'].iloc[i]
            rsi = vdf['rsi14'].iloc[i]
            atr = vdf['atr14'].iloc[i]
            
            if c_p < h_p and c > h and c > e and rsi < 70:
                in_trade = True; trade_dir = 1; entry_price = c; risk_dist = 2 * atr; sl = c - risk_dist
            elif c_p > h_p and c < h and c < e and rsi > 30:
                in_trade = True; trade_dir = -1; entry_price = c; risk_dist = 2 * atr; sl = c + risk_dist
                
    return np.array(r_multiples)

r_raw = backtest(False)
r_filt = backtest(True)

print(f"Raw Trades: {len(r_raw)}, PF: {r_raw[r_raw>0].sum()/abs(r_raw[r_raw<0].sum()):.2f}, Ret: {r_raw.sum():.1f}R")
print(f"Filt Trades: {len(r_filt)}, PF: {r_filt[r_filt>0].sum()/abs(r_filt[r_filt<0].sum()):.2f}, Ret: {r_filt.sum():.1f}R")
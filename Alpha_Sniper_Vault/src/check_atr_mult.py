import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize(): quit()

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

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi14'] = 100 - (100 / (1 + rs))

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()
vdf = df.dropna().copy()

def backtest(atr_mult):
    r_multiples = []
    in_trade = False
    trade_dir = 0
    entry_price = 0
    risk_dist = 0
    sl = 0
    
    # Gold spread+comm friction in dollars is ~$0.31 per oz.
    # We subtract the dollar friction directly from the PnL before calculating R!
    friction_dlr = 0.35 
    
    for i in range(1, len(vdf)):
        if in_trade:
            if trade_dir == 1 and vdf['low'].iloc[i] <= sl:
                loss_dollars = (entry_price - sl) + friction_dlr
                r_multiples.append(-loss_dollars / risk_dist)
                in_trade = False
            elif trade_dir == -1 and vdf['high'].iloc[i] >= sl:
                loss_dollars = (sl - entry_price) + friction_dlr
                r_multiples.append(-loss_dollars / risk_dist)
                in_trade = False
            elif trade_dir == 1 and vdf['close'].iloc[i] < vdf['hma100'].iloc[i]:
                win_dollars = (vdf['close'].iloc[i] - entry_price) - friction_dlr
                r_multiples.append(win_dollars / risk_dist)
                in_trade = False
            elif trade_dir == -1 and vdf['close'].iloc[i] > vdf['hma100'].iloc[i]:
                win_dollars = (entry_price - vdf['close'].iloc[i]) - friction_dlr
                r_multiples.append(win_dollars / risk_dist)
                in_trade = False
        else:
            c = vdf['close'].iloc[i]
            c_p = vdf['close'].iloc[i-1]
            h = vdf['hma100'].iloc[i]
            h_p = vdf['hma100'].iloc[i-1]
            e = vdf['ema200'].iloc[i]
            rsi = vdf['rsi14'].iloc[i]
            atr = vdf['atr14'].iloc[i]
            
            if c_p < h_p and c > h and c > e and rsi < 70:
                in_trade = True; trade_dir = 1; entry_price = c; risk_dist = atr_mult * atr; sl = c - risk_dist
            elif c_p > h_p and c < h and c < e and rsi > 30:
                in_trade = True; trade_dir = -1; entry_price = c; risk_dist = atr_mult * atr; sl = c + risk_dist
                
    r_arr = np.array(r_multiples)
    wins = r_arr[r_arr > 0]
    losses = r_arr[r_arr <= 0]
    wr = len(wins)/len(r_arr) if len(r_arr)>0 else 0
    pf = wins.sum() / abs(losses.sum()) if len(losses)>0 else 0
    return len(r_arr), wr, pf, r_arr.sum()

print("ATR=2.0:", backtest(2.0))
print("ATR=4.0:", backtest(4.0))
print("ATR=6.0:", backtest(6.0))
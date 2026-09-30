import pandas as pd
import numpy as np
import time
from numba import njit

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv"
df = pd.read_csv(csv_path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')

# Filtramos EXCLUSIVAMENTE el Régimen Moderno de Ruptura Secular (Post 2022)
df = df[df['time'] >= '2022-06-01'].copy()
df.reset_index(drop=True, inplace=True)

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma180'] = hma(df['close'], 180)
df['hma200'] = hma(df['close'], 200)
df['hma220'] = hma(df['close'], 220)

df['ema350'] = df['close'].ewm(span=350, adjust=False).mean()
df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()
df['ema450'] = df['close'].ewm(span=450, adjust=False).mean()

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
df['rsi14'] = 100 - (100 / (1 + (gain/loss)))

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()

df['hour'] = df['time'].dt.hour
df.dropna(inplace=True)

c, h, l = df['close'].values, df['high'].values, df['low'].values
rsi, atr, hours = df['rsi14'].values, df['atr14'].values, df['hour'].values

@njit
def fast_test(c, h, l, hma_arr, ema_arr, rsi_arr, atr_arr, hours_arr, atr_mult, friction):
    r_mults = []
    in_trade = False
    trade_dir = 0
    entry_price = sl = risk_dist = 0.0
    
    for i in range(1, len(c)):
        if in_trade:
            if trade_dir == 1 and l[i] <= sl:
                r_mults.append(-(entry_price - sl + friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and h[i] >= sl:
                r_mults.append(-(sl - entry_price + friction) / risk_dist)
                in_trade = False
            elif trade_dir == 1 and c[i] < hma_arr[i]:
                r_mults.append((c[i] - entry_price - friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and c[i] > hma_arr[i]:
                r_mults.append((entry_price - c[i] - friction) / risk_dist)
                in_trade = False
        else:
            hr = hours_arr[i]
            if hr < 12 or hr > 21: continue
            if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < 70:
                in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] - risk_dist
            elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > 30:
                in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] + risk_dist
                
    gp = sum([r for r in r_mults if r > 0])
    gl = sum([abs(r) for r in r_mults if r <= 0])
    pf = gp/gl if gl > 0 else 0
    return len(r_mults), pf, gp - gl

print("--- 1. NEIGHBORHOOD TEST (NO OVERFIT ZONE) ---")
for h_name, h_arr in [('180', df['hma180'].values), ('200', df['hma200'].values), ('220', df['hma220'].values)]:
    for e_name, e_arr in [('350', df['ema350'].values), ('400', df['ema400'].values), ('450', df['ema450'].values)]:
        t, pf, nr = fast_test(c, h, l, h_arr, e_arr, rsi, atr, hours, 1.5, 0.35)
        print(f"HMA {h_name} | EMA {e_name} => PF: {pf:.2f} | Net R: {nr:.1f}")

print("\n--- 2. SLIPPAGE & COMMISSION SHOCK TEST (HMA 200 / EMA 400) ---")
for fric in [0.35, 0.50, 0.75, 1.00]:
    t, pf, nr = fast_test(c, h, l, df['hma200'].values, df['ema400'].values, rsi, atr, hours, 1.5, fric)
    print(f"Friction: ${fric:.2f} => PF: {pf:.2f} | Net R: {nr:.1f}")

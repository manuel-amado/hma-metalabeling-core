import pandas as pd
import numpy as np
import time

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df = pd.read_csv(r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv")
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')
df.set_index('time', inplace=True)
df = df[df.index >= '2022-01-01']

c = df['close'].values
h = df['high'].values
l = df['low'].values
times = df.index.values

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
atr14 = df['tr'].rolling(14).mean().values

hma_periods = [100, 150, 200, 250, 300]
ema_periods = [200, 300, 400, 500, 600]

results = []

start_t = time.time()
print("Starting landscape optimization...")

# Precalculate indicators to save time
hmas = {p: hma(df['close'], p).values for p in hma_periods}
emas = {p: df['close'].ewm(span=p, adjust=False).mean().values for p in ema_periods}

for h_per in hma_periods:
    for e_per in ema_periods:
        hma_arr = hmas[h_per]
        ema_arr = emas[e_per]
        
        in_trade = False
        trade_dir = 0
        entry_price = sl = risk_dist = 0.0
        profits = []
        
        for i in range(1, len(c)):
            if in_trade:
                if trade_dir == 1 and l[i] <= sl:
                    profits.append(-risk_dist)
                    in_trade = False
                elif trade_dir == -1 and h[i] >= sl:
                    profits.append(-risk_dist)
                    in_trade = False
                elif trade_dir == 1 and c[i] < hma_arr[i]:
                    profits.append(c[i] - entry_price - 0.35)
                    in_trade = False
                elif trade_dir == -1 and c[i] > hma_arr[i]:
                    profits.append(entry_price - c[i] - 0.35)
                    in_trade = False
            else:
                if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i]:
                    in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = 1.5 * atr14[i]; sl = c[i] - risk_dist
                elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i]:
                    in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = 1.5 * atr14[i]; sl = c[i] + risk_dist
                    
        profits = np.array(profits)
        gross_profit = profits[profits > 0].sum()
        gross_loss = abs(profits[profits < 0].sum())
        pf = gross_profit / gross_loss if gross_loss > 0 else 0
        win_rate = (profits > 0).mean() * 100
        
        results.append({'HMA': h_per, 'EMA': e_per, 'Trades': len(profits), 'WinRate': win_rate, 'PF': pf})

df_res = pd.DataFrame(results)
print("\n--- MATRIZ DE ROBUSTEZ (PROFIT FACTOR) ---")
pivot_pf = df_res.pivot(index='HMA', columns='EMA', values='PF').round(2)
print(pivot_pf.to_string())

print("\n--- MATRIZ DE TRANSACCIONES ---")
pivot_tr = df_res.pivot(index='HMA', columns='EMA', values='Trades')
print(pivot_tr.to_string())
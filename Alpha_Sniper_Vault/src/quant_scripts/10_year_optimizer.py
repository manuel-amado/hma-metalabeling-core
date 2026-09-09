import pandas as pd
import numpy as np
import time
from numba import njit
import itertools

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv"
print("Loading 10-Year data...")
df = pd.read_csv(csv_path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')

print("Calculating base indicators (this takes a few seconds)...")
def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma100'] = hma(df['close'], 100)
df['hma200'] = hma(df['close'], 200)

df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi14'] = 100 - (100 / (1 + rs))

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()

df['hour'] = df['time'].dt.hour
df.dropna(inplace=True)

# Prepare numpy arrays for Numba
c = df['close'].values
h = df['high'].values
l = df['low'].values
o = df['open'].values

hma100 = df['hma100'].values
hma200 = df['hma200'].values
ema200 = df['ema200'].values
ema400 = df['ema400'].values
rsi14 = df['rsi14'].values
atr14 = df['atr14'].values
hours = df['hour'].values

@njit
def fast_backtest(c, h, l, hma_arr, ema_arr, rsi_arr, atr_arr, hours_arr, 
                  rsi_min, rsi_max, start_h, end_h, atr_mult, friction):
    r_multiples = []
    in_trade = False
    trade_dir = 0
    entry_price = 0.0
    risk_dist = 0.0
    sl = 0.0
    
    for i in range(1, len(c)):
        if in_trade:
            if trade_dir == 1 and l[i] <= sl:
                r_multiples.append(-(entry_price - sl + friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and h[i] >= sl:
                r_multiples.append(-(sl - entry_price + friction) / risk_dist)
                in_trade = False
            elif trade_dir == 1 and c[i] < hma_arr[i]:
                r_multiples.append((c[i] - entry_price - friction) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and c[i] > hma_arr[i]:
                r_multiples.append((entry_price - c[i] - friction) / risk_dist)
                in_trade = False
        else:
            hr = hours_arr[i]
            if hr < start_h or hr > end_h:
                continue
                
            c_curr = c[i]
            c_prev = c[i-1]
            hma_curr = hma_arr[i]
            hma_prev = hma_arr[i-1]
            ema_curr = ema_arr[i]
            rsi_curr = rsi_arr[i]
            atr_curr = atr_arr[i]
            
            if c_prev < hma_prev and c_curr > hma_curr and c_curr > ema_curr and rsi_curr < rsi_max:
                in_trade = True; trade_dir = 1; entry_price = c_curr; risk_dist = atr_mult * atr_curr; sl = c_curr - risk_dist
            elif c_prev > hma_prev and c_curr < hma_curr and c_curr < ema_curr and rsi_curr > rsi_min:
                in_trade = True; trade_dir = -1; entry_price = c_curr; risk_dist = atr_mult * atr_curr; sl = c_curr + risk_dist
                
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0
    for r in r_multiples:
        if r > 0: 
            wins += 1
            gross_profit += r
        else:
            losses += 1
            gross_loss += abs(r)
            
    total_trades = wins + losses
    wr = (wins / total_trades) if total_trades > 0 else 0
    pf = (gross_profit / gross_loss) if gross_loss > 0 else 0
    net_r = gross_profit - gross_loss
    
    return total_trades, wr, pf, net_r

# Grid Search Parameters
hma_choices = [hma100, hma200]
hma_names = ['100', '200']

ema_choices = [ema200, ema400]
ema_names = ['200', '400']

session_choices = [(0, 23), (8, 17), (12, 21)]
session_names = ['24H', 'London-NY', 'NY-Close']

atr_mults = [1.5, 2.0, 3.0, 4.0]

results = []
print("Starting grid search on 10 YEARS of data...")
start_time = time.time()

for (h_idx, h_arr) in enumerate(hma_choices):
    for (e_idx, e_arr) in enumerate(ema_choices):
        for s_idx, (st, en) in enumerate(session_choices):
            for am in atr_mults:
                t, wr, pf, net_r = fast_backtest(c, h, l, h_arr, e_arr, rsi14, atr14, hours, 
                                                30.0, 70.0, st, en, am, 0.35)
                if t > 500: # Ensure statistical significance
                    results.append({
                        'HMA': hma_names[h_idx],
                        'EMA': ema_names[e_idx],
                        'Session': session_names[s_idx],
                        'SL_ATR': am,
                        'Trades': t,
                        'WinRate': f"{wr*100:.1f}%",
                        'PF': f"{pf:.2f}",
                        'Net_R': f"{net_r:.1f}"
                    })

df_res = pd.DataFrame(results)
df_res['Net_R_val'] = df_res['Net_R'].astype(float)
df_res = df_res.sort_values(by='Net_R_val', ascending=False).drop(columns=['Net_R_val'])

report = "# 🧬 Optimización Universal (XAUUSD 10 Años: 2015-2026)\n\n"
report += "Buscando la configuración más robusta (Anti-Overfitting) para sobrevivir a todos los regímenes.\n\n"
report += df_res.head(15).to_markdown(index=False)
report += "\n\n**Tiempo de Computación:** {:.2f}s".format(time.time() - start_time)

with open(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\quant_scripts\10_year_optimization_results.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Optimization complete!")
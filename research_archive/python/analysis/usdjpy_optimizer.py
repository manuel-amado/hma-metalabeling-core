import pandas as pd
import numpy as np
import time
from numba import njit

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\USDJPY_M15_11Years.csv"
print("Loading USDJPY 11-Year data...")
df = pd.read_csv(csv_path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')

print("Calculating base indicators...")
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
c, h, l = df['close'].values, df['high'].values, df['low'].values
hma100, hma200 = df['hma100'].values, df['hma200'].values
ema200, ema400 = df['ema200'].values, df['ema400'].values
rsi14, atr14, hours = df['rsi14'].values, df['atr14'].values, df['hour'].values

@njit
def fast_backtest(c, h, l, hma_arr, ema_arr, rsi_arr, atr_arr, hours_arr, 
                  rsi_min, rsi_max, start_h, end_h, atr_mult, friction):
    r_multiples = []
    in_trade = False
    trade_dir = 0
    entry_price = sl = risk_dist = 0.0
    
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
                
            if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < rsi_max:
                in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] - risk_dist
            elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > rsi_min:
                in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] + risk_dist
                
    wins = losses = 0
    gross_profit = gross_loss = 0.0
    for r in r_multiples:
        if r > 0: 
            wins += 1; gross_profit += r
        else:
            losses += 1; gross_loss += abs(r)
            
    total_trades = wins + losses
    wr = (wins / total_trades) if total_trades > 0 else 0
    pf = (gross_profit / gross_loss) if gross_loss > 0 else 0
    net_r = gross_profit - gross_loss
    return total_trades, wr, pf, net_r

# Grid Search Parameters
hma_choices = [(hma100, '100'), (hma200, '200')]
ema_choices = [(ema200, '200'), (ema400, '400')]
session_choices = [((0, 23), '24H'), ((8, 21), 'London-NY'), ((0, 16), 'Tokyo-London'), ((12, 21), 'NY-Close')]
atr_mults = [1.5, 2.0, 3.0, 4.0]

# Friction for USDJPY: 1 pip = 0.010 in price. FTMO spread+comm is ~1 pip total.
friction_usd_jpy = 0.010

results = []
print("Starting grid search on USDJPY (11 YEARS)...")
start_time = time.time()

for h_arr, h_name in hma_choices:
    for e_arr, e_name in ema_choices:
        for (st, en), s_name in session_choices:
            for am in atr_mults:
                t, wr, pf, net_r = fast_backtest(c, h, l, h_arr, e_arr, rsi14, atr14, hours, 
                                                30.0, 70.0, st, en, am, friction_usd_jpy)
                if t > 500:
                    results.append({'HMA': h_name, 'EMA': e_name, 'Session': s_name, 'SL_ATR': am,
                                    'Trades': t, 'WinRate': f"{wr*100:.1f}%", 'PF': f"{pf:.2f}", 'Net_R': net_r})

df_res = pd.DataFrame(results).sort_values(by='Net_R', ascending=False)
report = "# 🧬 Optimización USDJPY (11 Años: 2015-2026)\n\n"
report += df_res.head(15).to_markdown(index=False)
with open(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\analysis\usdjpy_optimization.md", "w", encoding="utf-8") as f:
    f.write(report)
print("Optimization complete!")

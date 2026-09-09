import pandas as pd
import numpy as np

# 1. Load Data
df = pd.read_csv(r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv")
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')
df.set_index('time', inplace=True)
df = df[df.index >= '2022-01-01']

# 2. Indicators
def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma200'] = hma(df['close'], 200)
df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()
df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()

# Measure Impulse Energy (Distance from 20-bar lowest/highest)
df['lowest_20'] = df['low'].rolling(20).min()
df['highest_20'] = df['high'].rolling(20).max()

df.dropna(inplace=True)

# 3. Simulate Trades (Raw)
trades = []
in_trade = False
trade_dir = 0
entry_price = sl = risk_dist = 0.0
feat_impulse = 0.0

c = df['close'].values
h = df['high'].values
l = df['low'].values
hma_arr = df['hma200'].values
ema_arr = df['ema400'].values
atr_arr = df['atr14'].values
low_20 = df['lowest_20'].values
high_20 = df['highest_20'].values
hours = df.index.hour.values

for i in range(1, len(c)):
    if in_trade:
        if trade_dir == 1 and l[i] <= sl:
            trades.append({'dir': 1, 'impulse': feat_impulse, 'profit': -1.0})
            in_trade = False
        elif trade_dir == -1 and h[i] >= sl:
            trades.append({'dir': -1, 'impulse': feat_impulse, 'profit': -1.0})
            in_trade = False
        elif trade_dir == 1 and c[i] < hma_arr[i]:
            trades.append({'dir': 1, 'impulse': feat_impulse, 'profit': (c[i] - entry_price - 0.35) / risk_dist})
            in_trade = False
        elif trade_dir == -1 and c[i] > hma_arr[i]:
            trades.append({'dir': -1, 'impulse': feat_impulse, 'profit': (entry_price - c[i] - 0.35) / risk_dist})
            in_trade = False
    else:
        if 12 <= hours[i] <= 21:
            if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i]:
                in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = 1.4 * atr_arr[i]; sl = c[i] - risk_dist
                feat_impulse = (c[i] - low_20[i]) / atr_arr[i]
            elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i]:
                in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = 1.4 * atr_arr[i]; sl = c[i] + risk_dist
                feat_impulse = (high_20[i] - c[i]) / atr_arr[i]

tdf = pd.DataFrame(trades)
tdf['impulse_bin'] = pd.qcut(tdf['impulse'], q=5, labels=['Muy Corto', 'Corto', 'Medio', 'Largo', 'Extendido (Agotado)'])

print("=== AUDITORIA DE AGOTAMIENTO DE IMPULSO (V-SHAPE) ===")
res = tdf.groupby('impulse_bin').agg(
    Trades=('profit', 'count'), 
    WinRate=('profit', lambda x: (x>0).mean()*100), 
    PF_R=('profit', lambda x: x[x>0].sum() / abs(x[x<0].sum()) if abs(x[x<0].sum())>0 else 0)
).round(2)
print(res.to_string())

# Specific check for extreme impulses (> 4 ATRs)
extreme_trades = tdf[tdf['impulse'] > 4.0]
print("\n--- Trades con Impulso > 4 ATRs ---")
if len(extreme_trades) > 0:
    pf_ex = extreme_trades[extreme_trades['profit'] > 0]['profit'].sum() / abs(extreme_trades[extreme_trades['profit'] < 0]['profit'].sum())
    print(f"Trades: {len(extreme_trades)}, PF_R: {pf_ex:.2f}, WinRate: {(extreme_trades['profit'] > 0).mean()*100:.2f}%")
else:
    print("Ninguno.")

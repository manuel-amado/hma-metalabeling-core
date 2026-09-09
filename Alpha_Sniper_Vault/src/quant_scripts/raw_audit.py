import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

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
delta = df['close'].diff()
df['rsi14'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / (-delta.where(delta < 0, 0).rolling(14).mean()))))
df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()

# TR (True Range) for ADX
df['+dm'] = np.where((df['high'].diff() > df['low'].diff().abs()) & (df['high'].diff() > 0), df['high'].diff(), 0)
df['-dm'] = np.where((df['low'].diff().abs() > df['high'].diff()) & (df['low'].diff() < 0), df['low'].diff().abs(), 0)
df['+di'] = 100 * (df['+dm'].ewm(alpha=1/14, adjust=False).mean() / df['tr'].ewm(alpha=1/14, adjust=False).mean())
df['-di'] = 100 * (df['-dm'].ewm(alpha=1/14, adjust=False).mean() / df['tr'].ewm(alpha=1/14, adjust=False).mean())
df['dx'] = 100 * abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])
df['adx14'] = df['dx'].ewm(alpha=1/14, adjust=False).mean()

# Meta-Features
df['dist_ema'] = (df['close'] - df['ema400']) / df['atr14']
df['hma_slope'] = (df['hma200'] - df['hma200'].shift(5)) / df['atr14']
df['rsi_lookback_min'] = df['rsi14'].rolling(20).min()
df['rsi_lookback_max'] = df['rsi14'].rolling(20).max()

df.dropna(inplace=True)

# 3. Simulate Trades
trades = []
in_trade = False
trade_dir = 0
entry_price = sl = risk_dist = 0.0
feat_adx = feat_dist = feat_slope = 0.0
hour_filter = True # Simulate 24/7 or filtered? Let's do raw to get max sample size

c = df['close'].values
h = df['high'].values
l = df['low'].values
hma_arr = df['hma200'].values
ema_arr = df['ema400'].values
rsi_arr = df['rsi14'].values
rsi_min_arr = df['rsi_lookback_min'].values
rsi_max_arr = df['rsi_lookback_max'].values
atr_arr = df['atr14'].values
adx_arr = df['adx14'].values
dist_arr = df['dist_ema'].values
slope_arr = df['hma_slope'].values

for i in range(1, len(c)):
    if in_trade:
        if trade_dir == 1 and l[i] <= sl:
            trades.append({'dir': 1, 'adx': feat_adx, 'dist': feat_dist, 'slope': feat_slope, 'profit': -risk_dist})
            in_trade = False
        elif trade_dir == -1 and h[i] >= sl:
            trades.append({'dir': -1, 'adx': feat_adx, 'dist': feat_dist, 'slope': feat_slope, 'profit': -risk_dist})
            in_trade = False
        elif trade_dir == 1 and c[i] < hma_arr[i]:
            trades.append({'dir': 1, 'adx': feat_adx, 'dist': feat_dist, 'slope': feat_slope, 'profit': c[i] - entry_price - 0.35})
            in_trade = False
        elif trade_dir == -1 and c[i] > hma_arr[i]:
            trades.append({'dir': -1, 'adx': feat_adx, 'dist': feat_dist, 'slope': feat_slope, 'profit': entry_price - c[i] - 0.35})
            in_trade = False
    else:
        # Long Logic
        if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < 70 and rsi_min_arr[i] < 45:
            in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = 1.5 * atr_arr[i]; sl = c[i] - risk_dist
            feat_adx = adx_arr[i]; feat_dist = dist_arr[i]; feat_slope = slope_arr[i]
        # Short Logic
        elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > 30 and rsi_max_arr[i] > 55:
            in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = 1.5 * atr_arr[i]; sl = c[i] + risk_dist
            feat_adx = adx_arr[i]; feat_dist = dist_arr[i]; feat_slope = slope_arr[i]

tdf = pd.DataFrame(trades)

print("=== AUDITORIA DE COMPORTAMIENTO (SIN IA) ===")
# 1. ADX Analysis
tdf['adx_bin'] = pd.qcut(tdf['adx'], q=5, labels=['Muy Bajo', 'Bajo', 'Medio', 'Alto', 'Muy Alto'])
print("\n--- Rendimiento por Nivel de Tendencia (ADX) ---")
print(tdf.groupby('adx_bin').agg(Trades=('profit', 'count'), WinRate=('profit', lambda x: (x>0).mean()*100), PF=('profit', lambda x: x[x>0].sum() / abs(x[x<0].sum()) if abs(x[x<0].sum())>0 else 0)).round(2).to_string())

# 2. Distance to EMA Analysis
tdf['dist_bin'] = pd.qcut(tdf['dist'].abs(), q=5, labels=['Pegado a EMA', 'Cerca', 'Medio', 'Lejos', 'Extremo (Goma Estirada)'])
print("\n--- Rendimiento por Distancia a la EMA (Reversión a la Media) ---")
print(tdf.groupby('dist_bin').agg(Trades=('profit', 'count'), WinRate=('profit', lambda x: (x>0).mean()*100), PF=('profit', lambda x: x[x>0].sum() / abs(x[x<0].sum()) if abs(x[x<0].sum())>0 else 0)).round(2).to_string())

# 3. Slope Analysis
tdf['slope_bin'] = pd.qcut(tdf['slope'].abs(), q=5, labels=['Plano', 'Lento', 'Medio', 'Fuerte', 'Vertical'])
print("\n--- Rendimiento por Inclinación de la HMA (Momento) ---")
print(tdf.groupby('slope_bin').agg(Trades=('profit', 'count'), WinRate=('profit', lambda x: (x>0).mean()*100), PF=('profit', lambda x: x[x>0].sum() / abs(x[x<0].sum()) if abs(x[x<0].sum())>0 else 0)).round(2).to_string())

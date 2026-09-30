import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if not mt5.initialize(): quit()

# Get M15 Data
rates_m15 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 100000)
df_m15 = pd.DataFrame(rates_m15)
df_m15['time'] = pd.to_datetime(df_m15['time'], unit='s')
df_m15.set_index('time', inplace=True)

# Get D1 Data
rates_d1 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_D1, 0, 3000)
mt5.shutdown()

df_d1 = pd.DataFrame(rates_d1)
df_d1['time'] = pd.to_datetime(df_d1['time'], unit='s')
df_d1.set_index('time', inplace=True)

# Calculate D1 ADX
def rma(series, length):
    return series.ewm(alpha=1/length, adjust=False).mean()

df_d1['up_move'] = df_d1['high'] - df_d1['high'].shift(1)
df_d1['down_move'] = df_d1['low'].shift(1) - df_d1['low']
df_d1['plus_dm'] = np.where((df_d1['up_move'] > df_d1['down_move']) & (df_d1['up_move'] > 0), df_d1['up_move'], 0)
df_d1['minus_dm'] = np.where((df_d1['down_move'] > df_d1['up_move']) & (df_d1['down_move'] > 0), df_d1['down_move'], 0)
df_d1['tr'] = np.maximum(df_d1['high'] - df_d1['low'], np.maximum(abs(df_d1['high'] - df_d1['close'].shift(1)), abs(df_d1['low'] - df_d1['close'].shift(1))))

n = 14
df_d1['atr'] = rma(df_d1['tr'], n)
df_d1['plus_di'] = 100 * rma(df_d1['plus_dm'], n) / df_d1['atr']
df_d1['minus_di'] = 100 * rma(df_d1['minus_dm'], n) / df_d1['atr']
df_d1['dx'] = 100 * abs(df_d1['plus_di'] - df_d1['minus_di']) / (df_d1['plus_di'] + df_d1['minus_di'])
df_d1['adx'] = rma(df_d1['dx'], n)

# Map D1 ADX to M15 (shifted by 1 day to avoid lookahead bias!)
df_d1['adx_prev'] = df_d1['adx'].shift(1)
adx_series = df_d1['adx_prev'].reindex(df_m15.index.normalize(), method='ffill')
adx_series.index = df_m15.index
df_m15['d1_adx'] = adx_series

# M15 Indicators
def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df_m15['hma100'] = hma(df_m15['close'], 100)
df_m15['ema200'] = df_m15['close'].ewm(span=200, adjust=False).mean()

delta = df_m15['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df_m15['rsi14'] = 100 - (100 / (1 + rs))

df_m15['tr_m15'] = np.maximum(df_m15['high'] - df_m15['low'], np.maximum(abs(df_m15['high'] - df_m15['close'].shift(1)), abs(df_m15['low'] - df_m15['close'].shift(1))))
df_m15['atr14'] = df_m15['tr_m15'].rolling(14).mean()

# Drop NaNs
vdf = df_m15.dropna().copy()

# Backtest logic
def backtest(filter_adx=False):
    r_multiples = []
    equity = [100000]
    in_trade = False
    trade_dir = 0
    entry_price = 0
    sl = 0
    risk_dist = 0
    
    for i in range(1, len(vdf)):
        if in_trade:
            if trade_dir == 1 and vdf['low'].iloc[i] <= sl:
                r = -1.0
                r_multiples.append(r)
                equity.append(equity[-1] * (1 + (r * 0.01)))
                in_trade = False
            elif trade_dir == -1 and vdf['high'].iloc[i] >= sl:
                r = -1.0
                r_multiples.append(r)
                equity.append(equity[-1] * (1 + (r * 0.01)))
                in_trade = False
            elif trade_dir == 1 and vdf['close'].iloc[i] < vdf['hma100'].iloc[i]:
                r = (vdf['close'].iloc[i] - entry_price) / risk_dist
                r -= 0.0225 # 2.25% broker friction!
                r_multiples.append(r)
                equity.append(equity[-1] * (1 + (r * 0.01)))
                in_trade = False
            elif trade_dir == -1 and vdf['close'].iloc[i] > vdf['hma100'].iloc[i]:
                r = (entry_price - vdf['close'].iloc[i]) / risk_dist
                r -= 0.0225 # 2.25% broker friction!
                r_multiples.append(r)
                equity.append(equity[-1] * (1 + (r * 0.01)))
                in_trade = False
        else:
            if filter_adx and vdf['d1_adx'].iloc[i] < 20: continue
            
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
                
    return np.array(equity)

equity_raw = backtest(filter_adx=False)
equity_filtered = backtest(filter_adx=True)

# Plot
plt.figure(figsize=(14, 7))
plt.plot(np.linspace(0, len(equity_raw)-1, len(equity_raw)), equity_raw, label='XAUUSD M15 (Sin Filtro)', color='red', alpha=0.6)
plt.plot(np.linspace(0, len(equity_filtered)-1, len(equity_filtered)), equity_filtered, label='XAUUSD M15 (Filtro ADX>20 en D1)', color='green', linewidth=2)
plt.title("El Poder del Filtro de Regimen: Sobrevivir a 2022")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\regime_backtest.png')
print("Backtest plot done.")
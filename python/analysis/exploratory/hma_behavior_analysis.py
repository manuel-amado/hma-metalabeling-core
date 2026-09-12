import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize():
    print("MT5 initialization failed", mt5.last_error())
    quit()

print("Connected to MT5:", mt5.terminal_info().name)

# HMA Calculation function
def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    wma_half = wma(s, int(period / 2))
    wma_full = wma(s, period)
    diff = (2 * wma_half) - wma_full
    return wma(diff, int(np.sqrt(period)))

print("Fetching XAUUSD data...")
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 50000)
mt5.shutdown()

if rates is None:
    print("Failed to fetch rates.")
    quit()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)
df['close'] = df['close'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)

print("Calculating HMAs...")
df['HMA_50'] = hma(df['close'], 50)
df['HMA_200'] = hma(df['close'], 200)

df.dropna(inplace=True)

print("Analyzing HMA 50 Crosses...")
# Determine trend based on close vs HMA_50
df['Above_HMA50'] = df['close'] > df['HMA_50']
df['Cross_Up'] = (df['Above_HMA50'] == True) & (df['Above_HMA50'].shift(1) == False)
df['Cross_Down'] = (df['Above_HMA50'] == False) & (df['Above_HMA50'].shift(1) == True)

results_up = []
results_down = []

for idx in np.where(df['Cross_Up'])[0]:
    if idx + 20 >= len(df): continue
    # Analyze the next 20 bars (5 hours)
    future_high = df['high'].iloc[idx+1:idx+21].max()
    future_low = df['low'].iloc[idx+1:idx+21].min()
    entry_price = df['close'].iloc[idx]
    
    mfe = (future_high - entry_price) * 10 # points
    mae = (entry_price - future_low) * 10 # points
    results_up.append({'MFE': mfe, 'MAE': mae})

for idx in np.where(df['Cross_Down'])[0]:
    if idx + 20 >= len(df): continue
    future_high = df['high'].iloc[idx+1:idx+21].max()
    future_low = df['low'].iloc[idx+1:idx+21].min()
    entry_price = df['close'].iloc[idx]
    
    mfe = (entry_price - future_low) * 10 # points
    mae = (future_high - entry_price) * 10 # points
    results_down.append({'MFE': mfe, 'MAE': mae})

df_up = pd.DataFrame(results_up)
df_down = pd.DataFrame(results_down)

print("\n=== ANALISIS CUANTITATIVO: CRUCES HMA 50 (ORO M15) ===")
print("Ventana de Observacion: Siguientes 20 Velas (5 Horas)")
print(f"Total Cruces Alcistas: {len(df_up)}")
print(f"Promedio MFE (Max A Favor): {df_up['MFE'].mean():.1f} pts")
print(f"Promedio MAE (Max En Contra): {df_up['MAE'].mean():.1f} pts")

print(f"\nTotal Cruces Bajistas: {len(df_down)}")
print(f"Promedio MFE (Max A Favor): {df_down['MFE'].mean():.1f} pts")
print(f"Promedio MAE (Max En Contra): {df_down['MAE'].mean():.1f} pts")

# How many go at least 150 points in favor before 150 points against?
success_up = 0
for r in results_up:
    if r['MFE'] >= 150 and r['MAE'] < 100:
        success_up += 1
print(f"\nTasa de Momentum Fuerte (Alcista): {success_up/len(df_up)*100:.1f}%")

success_down = 0
for r in results_down:
    if r['MFE'] >= 150 and r['MAE'] < 100:
        success_down += 1
print(f"Tasa de Momentum Fuerte (Bajista): {success_down/len(df_down)*100:.1f}%")

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

if not mt5.initialize():
    print("MT5 Init Failed")
    quit()

# Fetch Daily data from 2015 to 2026
utc_from = datetime(2015, 1, 1)
utc_to = datetime(2026, 8, 30)
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_D1, utc_from, utc_to)
mt5.shutdown()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# 1. Calculate Choppiness Index (CHOP) 14
n = 14
df['tr'] = np.maximum(df['high'] - df['low'], 
                      np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                 abs(df['low'] - df['close'].shift(1))))
df['sum_tr'] = df['tr'].rolling(n).sum()
df['max_h'] = df['high'].rolling(n).max()
df['min_l'] = df['low'].rolling(n).min()
df['chop'] = 100 * np.log10(df['sum_tr'] / (df['max_h'] - df['min_l'])) / np.log10(n)

# 2. Calculate ADX 14
df['up_move'] = df['high'] - df['high'].shift(1)
df['down_move'] = df['low'].shift(1) - df['low']
df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

# Wilder's Smoothing
def rma(series, length):
    return series.ewm(alpha=1/length, adjust=False).mean()

df['atr'] = rma(df['tr'], n)
df['plus_di'] = 100 * rma(df['plus_dm'], n) / df['atr']
df['minus_di'] = 100 * rma(df['minus_dm'], n) / df['atr']
df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
df['adx'] = rma(df['dx'], n)

# Plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})

# Price
ax1.plot(df.index, df['close'], color='black', label='XAUUSD (Oro) Precio Diario')
ax1.axvspan(datetime(2015, 1, 1), datetime(2019, 1, 1), color='red', alpha=0.1, label='Rango 2015-2019 (Pérdidas)')
ax1.axvspan(datetime(2022, 1, 1), datetime(2023, 1, 1), color='orange', alpha=0.1, label='Rango 2022 (Pérdidas)')
ax1.axvspan(datetime(2024, 1, 1), datetime(2026, 1, 1), color='green', alpha=0.1, label='Tendencia 2024+ (Ganancias)')
ax1.legend(loc='upper left')
ax1.set_title('Análisis de Régimen Macro en XAUUSD (2015-2026)')
ax1.grid(True, alpha=0.3)

# CHOP
ax2.plot(df.index, df['chop'], color='blue', label='Choppiness Index (CHOP)')
ax2.axhline(61.8, color='red', linestyle='--', label='Rango (Consolidación)')
ax2.axhline(38.2, color='green', linestyle='--', label='Tendencia Fuerte')
ax2.fill_between(df.index, df['chop'], 61.8, where=(df['chop'] >= 61.8), color='red', alpha=0.3)
ax2.fill_between(df.index, df['chop'], 38.2, where=(df['chop'] <= 38.2), color='green', alpha=0.3)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# ADX
ax3.plot(df.index, df['adx'], color='purple', label='ADX (Fuerza de Tendencia)')
ax3.axhline(25, color='red', linestyle='--', label='Umbral de Tendencia (25)')
ax3.fill_between(df.index, df['adx'], 25, where=(df['adx'] < 25), color='red', alpha=0.3)
ax3.legend(loc='upper left')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\regime_analysis.png')
print("Análisis generado exitosamente.")
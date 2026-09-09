import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize():
    quit()

rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 50000)
mt5.shutdown()

df = pd.DataFrame(rates)
df['close'] = df['close'].astype(float)

def hma(s, period):
    weights = np.arange(1, period + 1)
    wma_half = s.rolling(int(period / 2)).apply(lambda x: np.dot(x, np.arange(1, int(period/2)+1)) / np.arange(1, int(period/2)+1).sum(), raw=True)
    wma_full = s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    diff = (2 * wma_half) - wma_full
    period_sqrt = int(np.sqrt(period))
    weights_sqrt = np.arange(1, period_sqrt + 1)
    return diff.rolling(period_sqrt).apply(lambda x: np.dot(x, weights_sqrt) / weights_sqrt.sum(), raw=True)

df['HMA_50'] = hma(df['close'], 50)
df['HMA_20'] = hma(df['close'], 20)
df.dropna(inplace=True)

# Analyze false reversals in HMA 20 during HMA 50 trends
df['Trend_50'] = np.where(df['HMA_50'] > df['HMA_50'].shift(1), 1, -1)
df['Trend_20'] = np.where(df['HMA_20'] > df['HMA_20'].shift(1), 1, -1)

# Count how many times HMA 20 reverses temporarily while HMA 50 keeps trending
false_reversals = 0
total_trends = 0

in_trend = False
current_trend_dir = 0
reversals_in_current_trend = 0

for i in range(1, len(df)):
    if df['Trend_50'].iloc[i] != df['Trend_50'].iloc[i-1]:
        # Trend changed
        if in_trend:
            total_trends += 1
            false_reversals += reversals_in_current_trend
        in_trend = True
        current_trend_dir = df['Trend_50'].iloc[i]
        reversals_in_current_trend = 0
    else:
        # Same trend
        if df['Trend_20'].iloc[i] != current_trend_dir and df['Trend_20'].iloc[i-1] == current_trend_dir:
            # HMA 20 just reversed against the HMA 50 trend
            reversals_in_current_trend += 1

print(f"Total HMA 50 Trends Analyzed: {total_trends}")
print(f"Total Temporary HMA 20 Reversals: {false_reversals}")
print(f"Average False Reversals per Trend: {false_reversals / total_trends:.2f}")

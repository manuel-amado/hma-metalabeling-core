import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import datetime
import os

if not mt5.initialize():
    print("Failed MT5 Init")
    quit()

# 1. Fetch Daily Data
utc_from = datetime.datetime(2015, 1, 1)
utc_to = datetime.datetime(2026, 12, 31)
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_D1, utc_from, utc_to)
mt5.shutdown()

if rates is None or len(rates) == 0:
    print("Failed to get D1 rates")
    quit()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# 2. Calculate Authentic ADX(14)
def rma(series, length):
    return series.ewm(alpha=1/length, adjust=False).mean()

df['up_move'] = df['high'] - df['high'].shift(1)
df['down_move'] = df['low'].shift(1) - df['low']
df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))

n = 14
df['atr'] = rma(df['tr'], n)
df['plus_di'] = 100 * rma(df['plus_dm'], n) / df['atr']
df['minus_di'] = 100 * rma(df['minus_dm'], n) / df['atr']
df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
df['adx'] = rma(df['dx'], n)

# Shift ADX by 1 day so MT5 OnTick (which is mid-day) uses the COMPLETED previous day's ADX!
# This prevents look-ahead bias in the backtest.
df['adx_signal'] = df['adx'].shift(1)

# 3. Generate MQL5 Include File
# We will create two arrays: one with timestamps (start of day), one with the boolean regime state.
# Regime = 1 if ADX_signal > 25, else 0.
df.dropna(subset=['adx_signal'], inplace=True)

mqh_content = "//+------------------------------------------------------------------+\n"
mqh_content += "//|                                                  RegimeMap.mqh   |\n"
mqh_content += "//|                            Generado automáticamente por Python   |\n"
mqh_content += "//+------------------------------------------------------------------+\n\n"

num_records = len(df)
mqh_content += f"int TOTAL_REGIME_RECORDS = {num_records};\n\n"
mqh_content += f"datetime RegimeDates[{num_records}] = {{\n"

dates_str = []
states_str = []

for _, row in df.iterrows():
    # Format: D'2015.01.01 00:00:00'
    d_str = row['time'].strftime("D'%Y.%m.%d 00:00:00'")
    dates_str.append(d_str)
    
    # State: 1 if ADX > 25 (Trend), 0 if ADX <= 25 (Range)
    state = 1 if row['adx_signal'] > 25.0 else 0
    states_str.append(str(state))

mqh_content += ",".join(dates_str) + "\n};\n\n"
mqh_content += f"int RegimeStates[{num_records}] = {{\n"
mqh_content += ",".join(states_str) + "\n};\n\n"

mqh_content += """
// Función de búsqueda binaria hiper-rápida para encontrar el régimen del día actual
int GetPrecomputedRegime(datetime current_time) {
    // Normalizamos el tiempo al inicio del día
    MqlDateTime dt;
    TimeToStruct(current_time, dt);
    dt.hour = 0; dt.min = 0; dt.sec = 0;
    datetime day_start = StructToTime(dt);
    
    int left = 0;
    int right = TOTAL_REGIME_RECORDS - 1;
    
    while(left <= right) {
        int mid = left + (right - left) / 2;
        if(RegimeDates[mid] == day_start) {
            return RegimeStates[mid];
        }
        if(RegimeDates[mid] < day_start) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    // Si no encuentra el día (ej. fines de semana), devuelve el último conocido
    if(right >= 0) return RegimeStates[right];
    return 1; // Default
}
"""

os.makedirs(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Include', exist_ok=True)
with open(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Include\RegimeMap.mqh', 'w') as f:
    f.write(mqh_content)

print(f"Generated RegimeMap.mqh with {num_records} daily records.")
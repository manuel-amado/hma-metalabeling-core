import MetaTrader5 as mt5
import pandas as pd

if not mt5.initialize():
    print("Failed to initialize MT5")
    quit()

rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 5)
mt5.shutdown()

if rates is not None:
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    print(df[['time', 'close', 'spread']])
else:
    print("No data retrieved.")
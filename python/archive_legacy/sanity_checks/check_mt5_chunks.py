import MetaTrader5 as mt5
import pandas as pd
import datetime

if not mt5.initialize(): quit()

# Try fetching 2018
utc_from = datetime.datetime(2018, 1, 1)
utc_to = datetime.datetime(2019, 1, 1)
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_M15, utc_from, utc_to)
if rates is None:
    print(f"Error fetching 2018: {mt5.last_error()}")
else:
    print(f"Fetched 2018: {len(rates)} bars")
    
# Try fetching 2024
utc_from = datetime.datetime(2024, 1, 1)
utc_to = datetime.datetime(2025, 1, 1)
rates2 = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_M15, utc_from, utc_to)
if rates2 is None:
    print(f"Error fetching 2024: {mt5.last_error()}")
else:
    print(f"Fetched 2024: {len(rates2)} bars")

mt5.shutdown()
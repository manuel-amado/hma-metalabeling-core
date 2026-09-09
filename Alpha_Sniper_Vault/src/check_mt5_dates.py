import MetaTrader5 as mt5
import datetime

if not mt5.initialize(): quit()

utc_from = datetime.datetime(2022, 1, 1)
utc_to = datetime.datetime(2026, 1, 1)
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_M15, utc_from, utc_to)
if rates is None:
    print(f"Failed to get by date. Error: {mt5.last_error()}")
else:
    print(f"Got {len(rates)} bars by date.")
mt5.shutdown()
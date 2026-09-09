import MetaTrader5 as mt5

if not mt5.initialize():
    print("Failed")
    quit()

rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 100000)
if rates is None:
    print(f"Failed to get 100k bars. Error: {mt5.last_error()}")
else:
    print(f"Got {len(rates)} bars.")

rates2 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 50000)
if rates2 is None:
    print(f"Failed to get 50k bars. Error: {mt5.last_error()}")
else:
    print(f"Got {len(rates2)} bars.")
mt5.shutdown()
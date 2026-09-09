import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

if not mt5.initialize():
    print("initialize() failed")
    quit()

symbols = ["XAUUSD", "USDJPY"]
timeframes = [
    (mt5.TIMEFRAME_M15, "M15"),
    (mt5.TIMEFRAME_H1, "H1"),
    (mt5.TIMEFRAME_H4, "H4")
]

date_from = datetime(2015, 1, 1)
date_to = datetime.now()

print("Testing MT5 Data Extraction...")
for sym in symbols:
    for tf, tf_name in timeframes:
        rates = mt5.copy_rates_range(sym, tf, date_from, date_to)
        if rates is None or len(rates) == 0:
            print(f"{sym} {tf_name}: Failed to get data.")
        else:
            print(f"{sym} {tf_name}: Extracted {len(rates)} bars.")

mt5.shutdown()
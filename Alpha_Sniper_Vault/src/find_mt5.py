import MetaTrader5 as mt5
import os

if mt5.initialize():
    data_path = mt5.terminal_info().data_path
    print(data_path)
    mt5.shutdown()
else:
    print("Failed")
import MetaTrader5 as mt5
import os

if mt5.initialize():
    info = mt5.terminal_info()
    print("Data path:", info.data_path)
    print("Common data path:", info.commondata_path)
    mt5.shutdown()
else:
    print("Failed")
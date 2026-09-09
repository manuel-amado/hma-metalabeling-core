import MetaTrader5 as mt5

if not mt5.initialize(): quit()

# Check HMA50 params if possible? MT5 Python API can't read custom indicator params.
# But we can check BTCUSD spread.
info = mt5.symbol_info("BTCUSD")
if info:
    print(f"Spread: {info.spread} points")
    print(f"Point: {info.point}")
    print(f"Trade Tick Size: {info.trade_tick_size}")
    print(f"Trade Tick Value: {info.trade_tick_value}")
mt5.shutdown()
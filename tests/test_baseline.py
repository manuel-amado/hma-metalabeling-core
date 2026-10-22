import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_OHLC_Dump_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
df = df.sort_values('Time').reset_index(drop=True)

df['Dir'] = np.where(df['Close'] > df['HMA50'], 1, -1)
df['Cross'] = (df['Dir'] != df['Dir'].shift(1)) & (df['Dir'].shift(1).notna())

df['SwingHigh20'] = (df['High'].shift(1).rolling(20).max() - df['Close']) / df['ATR14']
df['SwingLow20'] = (df['Close'] - df['Low'].shift(1).rolling(20).min()) / df['ATR14']

df = df.dropna(subset=['SwingHigh20', 'SwingLow20', 'Cross', 'ATR14']).reset_index(drop=True)

# Baseline Vectorized Backtest
trades = []
in_trade = False
trade_dir = 0
trade_sl_price = 0
trade_tp_price = 0
entry_price = 0

RR = 2.0
MIN_SL = 1.0
MAX_SL = 5.0

for i in range(len(df)):
    if df['Time'].iloc[i].year not in [2024, 2025]: continue
    
    if not in_trade:
        if df['Cross'].iloc[i]:
            in_trade = True
            trade_dir = df['Dir'].iloc[i]
            entry_price = df['Close'].iloc[i]
            
            atr = df['ATR14'].iloc[i]
            if trade_dir == 1: sl_atr = df['SwingLow20'].iloc[i]
            else: sl_atr = df['SwingHigh20'].iloc[i]
            sl_atr = np.clip(sl_atr, MIN_SL, MAX_SL)
            
            if trade_dir == 1:
                trade_sl_price = entry_price - (sl_atr * atr)
                trade_tp_price = entry_price + (sl_atr * RR * atr)
            else:
                trade_sl_price = entry_price + (sl_atr * atr)
                trade_tp_price = entry_price - (sl_atr * RR * atr)
    else:
        high = df['High'].iloc[i]
        low = df['Low'].iloc[i]
        
        hit_tp = False; hit_sl = False
        
        if trade_dir == 1:
            if low <= trade_sl_price: hit_sl = True
            if high >= trade_tp_price: hit_tp = True
        else:
            if high >= trade_sl_price: hit_sl = True
            if low <= trade_tp_price: hit_tp = True
            
        if hit_tp or hit_sl:
            if hit_sl: trades.append({'Win': 0, 'Risk': 1.0, 'Reward': -1.0})
            else: trades.append({'Win': 1, 'Risk': 1.0, 'Reward': RR})
            in_trade = False

res = pd.DataFrame(trades)
if len(res) > 0:
    win_rate = res['Win'].mean()
    profit_factor = (res[res['Win']==1]['Reward'].sum()) / (abs(res[res['Win']==0]['Reward'].sum()) + 1e-9)
    print(f"True Baseline (No AI, 1:2 RR) | Trades: {len(res)} | WR: {win_rate:.2%} | PF: {profit_factor:.2f}")


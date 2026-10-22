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

v3_df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
v3_df['Time'] = pd.to_datetime(v3_df['Time'], format='%Y.%m.%d %H:%M')
v3_df['Target'] = (v3_df['Target_Cross_Ret'] > 0.05).astype(int)

import xgboost as xgb
from sklearn.preprocessing import RobustScaler
df['Proba'] = 0.0

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

for test_year in [2024, 2025]:
    train_mask = (v3_df['Time'].dt.year.isin([test_year-2, test_year-1]))
    df_train = v3_df[train_mask].copy()
    if len(df_train) == 0: continue
    scaler = RobustScaler()
    X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
    model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
    model.fit(X_train_sc, df_train['Target'].values)
    test_mask = (df['Time'].dt.year == test_year)
    if test_mask.sum() > 0:
        X_test_sc = scaler.transform(df[test_mask][FEATURES].values)
        df.loc[test_mask, 'Proba'] = model.predict_proba(X_test_sc)[:, 1]

MIN_SL = 1.0; MAX_SL = 5.0
THRESH = 0.45; RR = 2.0
SPREAD = 0.30 # Approximate Gold Spread in points/dollars

trades = []
in_trade = False

for i in range(len(df)):
    if df['Time'].iloc[i].year not in [2024, 2025]: continue
    
    if not in_trade:
        if df['Cross'].iloc[i] and df['Proba'].iloc[i] >= THRESH:
            in_trade = True
            trade_dir = df['Dir'].iloc[i]
            # In MT5, entry is ask for Buy, bid for Sell
            entry_price = df['Close'].iloc[i] + SPREAD if trade_dir == 1 else df['Close'].iloc[i]
            
            atr = df['ATR14'].iloc[i]
            sl_atr = np.clip(df['SwingLow20'].iloc[i] if trade_dir == 1 else df['SwingHigh20'].iloc[i], MIN_SL, MAX_SL)
            
            # Anchor to previous close (how EA is coded right now)
            anchor = df['Close'].iloc[i]
            if trade_dir == 1:
                trade_sl_price = anchor - (sl_atr * atr)
                trade_tp_price = anchor + (sl_atr * RR * atr)
            else:
                trade_sl_price = anchor + (sl_atr * atr)
                trade_tp_price = anchor - (sl_atr * RR * atr)
    else:
        # High and Low are BID prices
        high_bid = df['High'].iloc[i]
        low_bid = df['Low'].iloc[i]
        high_ask = high_bid + SPREAD
        low_ask = low_bid + SPREAD
        
        hit_tp = False; hit_sl = False
        if trade_dir == 1:
            if low_bid <= trade_sl_price: hit_sl = True
            if high_bid >= trade_tp_price: hit_tp = True
        else:
            if high_ask >= trade_sl_price: hit_sl = True
            if low_ask <= trade_tp_price: hit_tp = True
            
        if hit_tp or hit_sl:
            if hit_sl: trades.append({'Win': 0, 'Risk': 1.0, 'Reward': -1.0})
            else: trades.append({'Win': 1, 'Risk': 1.0, 'Reward': RR})
            in_trade = False

res = pd.DataFrame(trades)
if len(res) > 0:
    win_rate = res['Win'].mean()
    profit_factor = (res[res['Win']==1]['Reward'].sum()) / (abs(res[res['Win']==0]['Reward'].sum()) + 1e-9)
    print(f"Spread Simulation | Trades: {len(res):4d} | WR: {win_rate:.2%} | PF: {profit_factor:.2f}")

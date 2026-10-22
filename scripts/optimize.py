import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_OHLC_Dump_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
df = df.sort_values('Time').reset_index(drop=True)

df['Slope10'] = (df['HMA10'] - df['HMA10'].shift(1)) / df['ATR14']
df['Slope21'] = (df['HMA21'] - df['HMA21'].shift(1)) / df['ATR14']
df['Slope50'] = (df['HMA50'] - df['HMA50'].shift(1)) / df['ATR14']
df['Slope100'] = (df['HMA100'] - df['HMA100'].shift(1)) / df['ATR14']
df['Slope200'] = (df['HMA200'] - df['HMA200'].shift(1)) / df['ATR14']

mean_hma = (df['HMA10'] + df['HMA21'] + df['HMA50'] + df['HMA100'] + df['HMA200']) / 5.0
sum_sq = (df['HMA10']-mean_hma)**2 + (df['HMA21']-mean_hma)**2 + (df['HMA50']-mean_hma)**2 + (df['HMA100']-mean_hma)**2 + (df['HMA200']-mean_hma)**2
df['RibbonSpread'] = np.sqrt(sum_sq / 5.0) / df['ATR14']

cond_align_1 = (df['HMA10'] > df['HMA21']) & (df['HMA21'] > df['HMA50']) & (df['HMA50'] > df['HMA100']) & (df['HMA100'] > df['HMA200'])
cond_align_neg1 = (df['HMA10'] < df['HMA21']) & (df['HMA21'] < df['HMA50']) & (df['HMA50'] < df['HMA100']) & (df['HMA100'] < df['HMA200'])
df['RibbonAlign'] = np.where(cond_align_1, 1, np.where(cond_align_neg1, -1, 0))

df['DistH4'] = (df['Close'] - df['EMAH4']) / df['ATR14']
df['DistD1'] = (df['Close'] - df['EMAD1']) / df['ATR14']
df['MTFATR'] = 1.0 

df['CandleVel'] = (df['Close'] - df['Open']) / df['ATR14']
cdl_range = df['High'] - df['Low']
df['CandleDom'] = np.where(cdl_range > 0, (df['Close'] - df['Open']) / cdl_range, 0)

sma20 = df['Close'].rolling(20).mean()
std20 = df['Close'].rolling(20).std()
df['ZScore'] = np.where(std20 > 0, (df['Close'] - sma20) / std20, 0)

df['Dir'] = np.where(df['Close'] > df['HMA50'], 1, -1)
df['Cross'] = (df['Dir'] != df['Dir'].shift(1)) & (df['Dir'].shift(1).notna())

snapbacks = []
time_in_trend = []
curr_snap = 0
curr_time = 0
for i in range(len(df)):
    if pd.isna(df['Dir'].iloc[i]):
        snapbacks.append(0); time_in_trend.append(0); continue
    if i > 0 and df['Dir'].iloc[i] != df['Dir'].iloc[i-1]:
        curr_snap = 0; curr_time = 0
    dist = abs(df['Close'].iloc[i] - df['HMA50'].iloc[i]) / df['ATR14'].iloc[i]
    if dist > curr_snap: curr_snap = dist
    curr_time += 1
    snapbacks.append(curr_snap)
    time_in_trend.append(curr_time)
df['Snapback'] = snapbacks
df['TimeInTrend'] = time_in_trend

high10 = df['High'].rolling(10).max()
low10 = df['Low'].rolling(10).min()
df['PainIndex'] = np.where(df['Dir'] == 1, (df['Close'] - high10)/df['ATR14'], (df['Close'] - low10)/df['ATR14'])

delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

df['SwingHigh20'] = (df['High'].shift(1).rolling(20).max() - df['Close']) / df['ATR14']
df['SwingLow20'] = (df['Close'] - df['Low'].shift(1).rolling(20).min()) / df['ATR14']

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

df = df.dropna(subset=FEATURES + ['SwingHigh20', 'SwingLow20', 'Cross']).reset_index(drop=True)

v3_df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
v3_df['Time'] = pd.to_datetime(v3_df['Time'], format='%Y.%m.%d %H:%M')
v3_df['Target'] = (v3_df['Target_Cross_Ret'] > 0.05).astype(int)

df['Proba'] = 0.0

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

MIN_SL = 1.0
MAX_SL = 5.0

print("--- Optimization Grid ---")
for THRESH in [0.30, 0.35, 0.40]:
    for RR in [1.5, 2.0, 2.5, 3.0]:
        trades = []
        in_trade = False
        trade_dir = 0; trade_sl_price = 0; trade_tp_price = 0
        for i in range(len(df)):
            if df['Time'].iloc[i].year not in [2024, 2025]: continue
            if not in_trade:
                if df['Cross'].iloc[i] and df['Proba'].iloc[i] >= THRESH:
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
                high = df['High'].iloc[i]; low = df['Low'].iloc[i]
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
            print(f"Thresh: {THRESH:.2f} | RR: {RR:.1f} | Trades: {len(res):4d} | WR: {win_rate:.2%} | PF: {profit_factor:.2f}")

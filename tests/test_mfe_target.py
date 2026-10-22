import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_OHLC_Dump_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
df = df.sort_values('Time').reset_index(drop=True)

# 1. Feature Engineering
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

df['CandleVel'] = (df['Close'] - df['Open']) / df['ATR14']
cdl_range = df['High'] - df['Low']
df['CandleDom'] = np.where(cdl_range > 0, (df['Close'] - df['Open']) / cdl_range, 0)
df['Dir'] = np.where(df['Close'] > df['HMA50'], 1, -1)
df['Cross'] = (df['Dir'] != df['Dir'].shift(1)) & (df['Dir'].shift(1).notna())

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'CandleVel', 'CandleDom']

# Only keep crosses
crosses = df[df['Cross']].copy()
cross_indices = crosses.index.values

# 2. Build the Exact MFE/MAE Target for 1:2 RR
print("Building True Target Matrix...")
targets = []
for idx in cross_indices:
    trade_dir = df['Dir'].iloc[idx]
    entry = df['Close'].iloc[idx]
    atr = df['ATR14'].iloc[idx]
    
    # We define standard 1:2 RR from entry: SL = 1.5 ATR, TP = 3.0 ATR
    SL_DIST = 1.5
    TP_DIST = 3.0
    
    if trade_dir == 1:
        tp_price = entry + (TP_DIST * atr)
        sl_price = entry - (SL_DIST * atr)
    else:
        tp_price = entry - (TP_DIST * atr)
        sl_price = entry + (SL_DIST * atr)
        
    hit_tp = False
    hit_sl = False
    
    # Scan forward max 96 bars (24 hours)
    for j in range(1, 97):
        if idx + j >= len(df): break
        high = df['High'].iloc[idx + j]
        low = df['Low'].iloc[idx + j]
        
        if trade_dir == 1:
            if low <= sl_price: hit_sl = True
            if high >= tp_price: hit_tp = True
        else:
            if high >= sl_price: hit_sl = True
            if low <= tp_price: hit_tp = True
            
        if hit_tp or hit_sl:
            break
            
    # Target 1 if hit TP before SL, 0 otherwise
    if hit_tp and not hit_sl: targets.append(1)
    else: targets.append(0)

crosses['Target'] = targets
crosses = crosses.dropna(subset=FEATURES).copy()

print(f"Total labeled crosses: {len(crosses)} | Win Rate Baseline: {crosses['Target'].mean():.2%}")

# 3. Simulate WFO and count trades
crosses['Proba'] = 0.0

for test_year in [2024, 2025]:
    train_mask = (crosses['Time'].dt.year.isin([test_year-2, test_year-1]))
    df_train = crosses[train_mask].copy()
    if len(df_train) == 0: continue
    
    scaler = RobustScaler()
    X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
    
    # Light class weight because Target 1 is ~20%
    weight = (len(df_train) - df_train['Target'].sum()) / df_train['Target'].sum()
    
    model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, 
                              scale_pos_weight=weight, random_state=42)
    model.fit(X_train_sc, df_train['Target'].values)
    
    test_mask = (crosses['Time'].dt.year == test_year)
    if test_mask.sum() > 0:
        X_test_sc = scaler.transform(crosses[test_mask][FEATURES].values)
        crosses.loc[test_mask, 'Proba'] = model.predict_proba(X_test_sc)[:, 1]

test_df = crosses[crosses['Time'].dt.year.isin([2024, 2025])]

for thresh in [0.5, 0.6, 0.7, 0.8]:
    selected = test_df[test_df['Proba'] >= thresh]
    if len(selected) > 0:
        wr = selected['Target'].mean()
        pf = (selected['Target'].sum() * 2.0) / ((len(selected) - selected['Target'].sum()) * 1.0 + 1e-9)
        print(f"Thresh: {thresh:.2f} | Trades: {len(selected):4d} | WR: {wr:.2%} | Expected PF: {pf:.2f}")


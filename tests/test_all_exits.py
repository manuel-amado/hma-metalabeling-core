import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import warnings
warnings.filterwarnings('ignore')

# 1. Load Data
df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_OHLC_Dump_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
df = df.sort_values('Time').reset_index(drop=True)

# 2. Features
df['Slope10'] = (df['HMA10'] - df['HMA10'].shift(1)) / df['ATR14']
df['Slope21'] = (df['HMA21'] - df['HMA21'].shift(1)) / df['ATR14']
df['Slope50'] = (df['HMA50'] - df['HMA50'].shift(1)) / df['ATR14']
df['Slope100'] = (df['HMA100'] - df['HMA100'].shift(1)) / df['ATR14']
df['Slope200'] = (df['HMA200'] - df['HMA200'].shift(1)) / df['ATR14']

mean_hma = (df['HMA10'] + df['HMA21'] + df['HMA50'] + df['HMA100'] + df['HMA200']) / 5.0
sum_sq = (df['HMA10']-mean_hma)**2 + (df['HMA21']-mean_hma)**2 + (df['HMA50']-mean_hma)**2 + (df['HMA100']-mean_hma)**2 + (df['HMA200']-mean_hma)**2
df['RibbonSpread'] = np.sqrt(sum_sq / 5.0) / df['ATR14']
df['RibbonSpreadRaw'] = np.sqrt(sum_sq / 5.0) # Used for Ribbon Exit

cond_align_1 = (df['HMA10'] > df['HMA21']) & (df['HMA21'] > df['HMA50']) & (df['HMA50'] > df['HMA100']) & (df['HMA100'] > df['HMA200'])
cond_align_neg1 = (df['HMA10'] < df['HMA21']) & (df['HMA21'] < df['HMA50']) & (df['HMA50'] < df['HMA100']) & (df['HMA100'] < df['HMA200'])
df['RibbonAlign'] = np.where(cond_align_1, 1, np.where(cond_align_neg1, -1, 0))

df['DistH4'] = (df['Close'] - df['EMAH4']) / df['ATR14']
df['DistD1'] = (df['Close'] - df['EMAD1']) / df['ATR14']
df['MTFATR'] = 1.0 

df['CandleVel'] = (df['Close'] - df['Open']) / df['ATR14']
cdl_range = df['High'] - df['Low']
df['CandleDom'] = np.where(cdl_range > 0, (df['Close'] - df['Open']) / cdl_range, 0)
df['ZScore'] = np.where(df['Close'].rolling(20).std() > 0, (df['Close'] - df['Close'].rolling(20).mean()) / df['Close'].rolling(20).std(), 0)

df['Dir'] = np.where(df['Close'] > df['HMA50'], 1, -1)
df['Cross'] = (df['Dir'] != df['Dir'].shift(1)) & (df['Dir'].shift(1).notna())

snapbacks = []; time_in_trend = []; curr_snap = 0; curr_time = 0
for i in range(len(df)):
    if pd.isna(df['Dir'].iloc[i]):
        snapbacks.append(0); time_in_trend.append(0); continue
    if i > 0 and df['Dir'].iloc[i] != df['Dir'].iloc[i-1]:
        curr_snap = 0; curr_time = 0
    dist = abs(df['Close'].iloc[i] - df['HMA50'].iloc[i]) / df['ATR14'].iloc[i]
    if dist > curr_snap: curr_snap = dist
    curr_time += 1
    snapbacks.append(curr_snap); time_in_trend.append(curr_time)
df['Snapback'] = snapbacks; df['TimeInTrend'] = time_in_trend
df['PainIndex'] = np.where(df['Dir'] == 1, (df['Close'] - df['High'].rolling(10).max())/df['ATR14'], (df['Close'] - df['Low'].rolling(10).min())/df['ATR14'])

delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
df['RSI'] = 100 - (100 / (1 + gain/loss))

df['SwingHigh20'] = (df['High'].shift(1).rolling(20).max() - df['Close']) / df['ATR14']
df['SwingLow20'] = (df['Close'] - df['Low'].shift(1).rolling(20).min()) / df['ATR14']

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

df = df.dropna(subset=FEATURES + ['SwingHigh20', 'SwingLow20', 'Cross']).reset_index(drop=True)

# 3. XGBoost Filtering (WFO on Target_Cross_Ret > 0.05)
v3_df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
v3_df['Time'] = pd.to_datetime(v3_df['Time'], format='%Y.%m.%d %H:%M')
v3_df['Target'] = (v3_df['Target_Cross_Ret'] > 0.05).astype(int)

df['Proba'] = 0.0
for test_year in [2024, 2025, 2026]:
    # We use 2024-2025 to predict 2026 as well
    train_yr1 = test_year - 2 if test_year != 2026 else 2024
    train_yr2 = test_year - 1 if test_year != 2026 else 2025
    train_mask = (v3_df['Time'].dt.year.isin([train_yr1, train_yr2]))
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

# 4. Simulation Engine
MIN_SL = 2.0; MAX_SL = 5.0
THRESH = 0.45; SPREAD = 0.30

# Find all entries
entries = df[(df['Time'].dt.year.isin([2024, 2025, 2026])) & (df['Cross']) & (df['Proba'] >= THRESH)].copy()
entry_indices = entries.index.values

print(f"Total Filtered Entries (2024-2026): {len(entry_indices)}\n")

strategies = {
    '1:2_Fixed': {'Desc': 'Classic 1:2 R:R (The Baseline)'},
    '1:1_Fixed': {'Desc': 'Classic 1:1 R:R (Secure Profits Faster)'},
    '1:2_Breakeven': {'Desc': '1:2 R:R, SL to Breakeven at 1:1'},
    'Ribbon_Exit': {'Desc': 'Exit if Ribbon Compresses 30% from peak'},
    'Trailing_ATR': {'Desc': 'Trail SL at Peak MFE - 2.0 ATR'}
}

results = {k: [] for k in strategies.keys()}

for idx in entry_indices:
    trade_dir = df['Dir'].iloc[idx]
    entry_close = df['Close'].iloc[idx]
    entry_price = entry_close + SPREAD if trade_dir == 1 else entry_close
    atr = df['ATR14'].iloc[idx]
    
    sl_atr = np.clip(df['SwingLow20'].iloc[idx] if trade_dir == 1 else df['SwingHigh20'].iloc[idx], MIN_SL, MAX_SL)
    sl_dist = sl_atr * atr
    
    init_sl = entry_price - sl_dist if trade_dir == 1 else entry_price + sl_dist
    
    # Trackers
    pnl = {k: None for k in strategies.keys()}
    sl = {'1:2_Fixed': init_sl, '1:1_Fixed': init_sl, '1:2_Breakeven': init_sl, 'Ribbon_Exit': init_sl, 'Trailing_ATR': init_sl}
    tp = {
        '1:2_Fixed': entry_price + (sl_dist * 2.0) if trade_dir == 1 else entry_price - (sl_dist * 2.0),
        '1:1_Fixed': entry_price + (sl_dist * 1.0) if trade_dir == 1 else entry_price - (sl_dist * 1.0),
        '1:2_Breakeven': entry_price + (sl_dist * 2.0) if trade_dir == 1 else entry_price - (sl_dist * 2.0),
        'Ribbon_Exit': 0, # No TP
        'Trailing_ATR': 0 # No TP
    }
    mfe_price = entry_price
    max_ribbon = df['RibbonSpreadRaw'].iloc[idx]
    
    # Forward pass
    for i in range(idx+1, min(idx+200, len(df))):
        high_bid = df['High'].iloc[i]; low_bid = df['Low'].iloc[i]
        high_ask = high_bid + SPREAD; low_ask = low_bid + SPREAD
        ribbon = df['RibbonSpreadRaw'].iloc[i]
        
        if ribbon > max_ribbon: max_ribbon = ribbon
        
        for k in pnl.keys():
            if pnl[k] is not None: continue # Already closed
            
            # Check Stops and Limits
            hit_sl = False; hit_tp = False
            if trade_dir == 1:
                if low_bid <= sl[k]: hit_sl = True
                if tp[k] != 0 and high_bid >= tp[k]: hit_tp = True
            else:
                if high_ask >= sl[k]: hit_sl = True
                if tp[k] != 0 and low_ask <= tp[k]: hit_tp = True
                
            if hit_sl: pnl[k] = sl[k] - entry_price if trade_dir == 1 else entry_price - sl[k]
            elif hit_tp: pnl[k] = tp[k] - entry_price if trade_dir == 1 else entry_price - tp[k]
            else:
                # Dynamic Logic
                if k == '1:2_Breakeven':
                    # Check 1:1 threshold
                    thresh = entry_price + sl_dist if trade_dir == 1 else entry_price - sl_dist
                    if trade_dir == 1 and high_bid >= thresh: sl[k] = entry_price
                    if trade_dir == -1 and low_ask <= thresh: sl[k] = entry_price
                
                elif k == 'Trailing_ATR':
                    if trade_dir == 1 and high_bid > mfe_price:
                        mfe_price = high_bid
                        new_sl = mfe_price - (2.0 * df['ATR14'].iloc[i])
                        if new_sl > sl[k]: sl[k] = new_sl
                    if trade_dir == -1 and low_ask < mfe_price:
                        mfe_price = low_ask
                        new_sl = mfe_price + (2.0 * df['ATR14'].iloc[i])
                        if new_sl < sl[k]: sl[k] = new_sl
                
                elif k == 'Ribbon_Exit':
                    # Compression by 30%
                    if ribbon < max_ribbon * 0.70:
                        # Exit at current close
                        close_price = df['Close'].iloc[i] + SPREAD if trade_dir == -1 else df['Close'].iloc[i]
                        pnl[k] = close_price - entry_price if trade_dir == 1 else entry_price - close_price
                        
        # Break if all closed
        if all(v is not None for v in pnl.values()): break
        
    for k in pnl.keys():
        if pnl[k] is None:
            close_price = df['Close'].iloc[idx+199]
            pnl[k] = close_price - entry_price if trade_dir == 1 else entry_price - close_price
        # Normalize PnL to R units
        results[k].append(pnl[k] / sl_dist)

print("=== EXIT STRATEGY TOURNAMENT (2024 - 2026) ===")
for k in strategies.keys():
    res = np.array(results[k])
    wins = (res > 0).sum()
    losses = (res <= 0).sum()
    wr = wins / len(res)
    gross_win = res[res > 0].sum()
    gross_loss = abs(res[res <= 0].sum())
    pf = gross_win / (gross_loss + 1e-9)
    net_r = gross_win - gross_loss
    print(f"{strategies[k]['Desc'][:35]:<35} | WR: {wr:.2%} | PF: {pf:.2f} | Net R: {net_r:6.2f} R")


import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')

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

df['Dir'] = np.where(df['Close'] > df['HMA50'], 1, -1)
df['Cross'] = (df['Dir'] != df['Dir'].shift(1)) & (df['Dir'].shift(1).notna())

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1']

df = df.dropna(subset=FEATURES + ['Cross']).reset_index(drop=True)
crosses = df[df['Cross']].copy()
cross_indices = crosses.index.values

barrier_grid = [{'SL': 1.0, 'TP': 1.0, 'R': 1.0}, 
                {'SL': 1.0, 'TP': 2.0, 'R': 2.0}, 
                {'SL': 2.0, 'TP': 2.0, 'R': 1.0}, 
                {'SL': 2.0, 'TP': 4.0, 'R': 2.0}]

all_targets = np.zeros((len(cross_indices), 4))
returns = np.zeros((len(cross_indices), 4))

print("Labeling Meta-Classes...")
for idx_enum, idx in enumerate(cross_indices):
    trade_dir = df['Dir'].iloc[idx]
    entry = df['Close'].iloc[idx]
    atr = df['ATR14'].iloc[idx]
    
    for i, b in enumerate(barrier_grid):
        SL_DIST = b['SL']; TP_DIST = b['TP']; R = b['R']
        tp_price = entry + (TP_DIST * atr) if trade_dir == 1 else entry - (TP_DIST * atr)
        sl_price = entry - (SL_DIST * atr) if trade_dir == 1 else entry + (SL_DIST * atr)
            
        hit_tp = False; hit_sl = False
        for j in range(1, 97):
            if idx + j >= len(df): break
            high = df['High'].iloc[idx + j]; low = df['Low'].iloc[idx + j]
            if trade_dir == 1:
                if low <= sl_price: hit_sl = True
                if high >= tp_price: hit_tp = True
            else:
                if high >= sl_price: hit_sl = True
                if low <= tp_price: hit_tp = True
            if hit_tp or hit_sl: break
                
        if hit_tp and not hit_sl:
            all_targets[idx_enum, i] = 1
            returns[idx_enum, i] = R
        else:
            all_targets[idx_enum, i] = 0
            returns[idx_enum, i] = -1.0 # Risk is 1 unit of SL

# The optimal class is the one that gives the highest return
# If multiple give same return, we prefer the one with smaller SL (i=1 over i=3)
optimal_class = np.argmax(returns, axis=1)
# If the max return is <= 0, it means all barriers failed. We label it as class 4 (NO TRADE).
no_trade = np.max(returns, axis=1) <= 0
optimal_class[no_trade] = 4

crosses['MetaClass'] = optimal_class

print("Meta-Classes Distribution:")
print(crosses['MetaClass'].value_counts(normalize=True))

# Drop Class 4 (No Trade) for training, or keep it to learn when to skip!
# If we keep it, it's a 5-class problem. Class 4 will dominate (since 50%+ fail all barriers).

train_df = crosses[crosses['Time'].dt.year <= 2024]
test_df = crosses[crosses['Time'].dt.year >= 2025]

scaler = RobustScaler()
X_train = scaler.fit_transform(train_df[FEATURES].values)
y_train = train_df['MetaClass'].values

X_test = scaler.transform(test_df[FEATURES].values)
y_test = test_df['MetaClass'].values

# Compute class weights manually
class_weights = {}
counts = np.bincount(y_train)
for i, count in enumerate(counts):
    class_weights[i] = len(y_train) / (len(counts) * (count + 1e-9))
sample_weights = np.array([class_weights[y] for y in y_train])

print("Training Multi-Class Meta-Model...")
model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, objective='multi:softprob')
model.fit(X_train, y_train, sample_weight=sample_weights)

preds = model.predict(X_test)
print("\nClassification Report (2025-2026 OOS):")
print(classification_report(y_test, preds))

# Simulate the Dynamic Metalabeled Strategy in OOS!
# If pred == 4, we don't trade.
# If pred == 0, we trade with SL 1, TP 1
# If pred == 1, we trade with SL 1, TP 2
# If pred == 2, we trade with SL 2, TP 2
# If pred == 3, we trade with SL 2, TP 4

trades_taken = 0
pnl_r = 0.0
for i in range(len(test_df)):
    pred = preds[i]
    if pred == 4: continue # Skip bad trades
    
    trades_taken += 1
    # Check if the predicted barrier was actually hit successfully
    # all_targets contains whether barrier was successful (1) or not (0)
    actual_idx_in_all = np.where(crosses.index == test_df.index[i])[0][0]
    
    success = all_targets[actual_idx_in_all, pred]
    
    if success == 1:
        pnl_r += barrier_grid[pred]['R']
    else:
        pnl_r -= 1.0 # Lost 1 risk unit

print(f"\nDynamic Metalabeling Performance (2025-2026):")
print(f"Trades Taken: {trades_taken} / {len(test_df)}")
print(f"Net Profit (R): {pnl_r:.2f} R")


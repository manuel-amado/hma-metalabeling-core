import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import ParameterGrid
import warnings
warnings.filterwarnings('ignore')

print("Loading Data for Triple Barrier...")
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

print(f"Total Crosses: {len(cross_indices)}")

# Simulate multiple barriers to find the optimal dynamic target
barrier_grid = [{'SL': 1.0, 'TP': 1.0}, {'SL': 1.0, 'TP': 2.0}, {'SL': 2.0, 'TP': 2.0}, {'SL': 2.0, 'TP': 4.0}]
results_list = []

print("Simulating Triple Barriers...")
for i, b in enumerate(barrier_grid):
    SL_DIST = b['SL']
    TP_DIST = b['TP']
    targets = []
    
    for idx in cross_indices:
        trade_dir = df['Dir'].iloc[idx]
        entry = df['Close'].iloc[idx]
        atr = df['ATR14'].iloc[idx]
        
        tp_price = entry + (TP_DIST * atr) if trade_dir == 1 else entry - (TP_DIST * atr)
        sl_price = entry - (SL_DIST * atr) if trade_dir == 1 else entry + (SL_DIST * atr)
            
        hit_tp = False; hit_sl = False
        
        # Max hold time: 96 bars (24 hours)
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
                
        if hit_tp and not hit_sl: targets.append(1)
        else: targets.append(0)
        
    crosses[f"Target_{i}"] = targets
    print(f"Barrier {i} (SL {SL_DIST}, TP {TP_DIST}) | WR: {np.mean(targets):.2%}")


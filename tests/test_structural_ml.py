import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V2_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['SL_ATR'] = np.where(df['Dir'] == 1, df['SwingLow20'], df['SwingHigh20'])
df['SL_ATR'] = df['SL_ATR'].clip(lower=1.0, upper=5.0)
df['TP_ATR'] = df['SL_ATR'] * 1.5

sl_hit = df['MAE_ATR'] <= -df['SL_ATR']
tp_hit = df['MFE_ATR'] >= df['TP_ATR']
df['Target'] = (tp_hit & (~sl_hit)).astype(int)

print(f"Target Distribution: {df['Target'].mean():.2%}")

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

train_mask = (df['Time'].dt.year.isin([2022, 2023]))
test_mask = (df['Time'].dt.year == 2024)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

scaler = RobustScaler()
X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
X_test_sc = scaler.transform(df_test[FEATURES].values)

model = xgb.XGBClassifier(max_depth=3, learning_rate=0.05, n_estimators=100, random_state=42)
model.fit(X_train_sc, df_train['Target'].values)

probas = model.predict_proba(X_test_sc)[:, 1]
df_test['Proba'] = probas

print("--- OOS (2024) Structural TP/SL Filtering ---")
for threshold in [0.20, 0.25, 0.30, 0.35]:
    selected = df_test[df_test['Proba'] >= threshold]
    if len(selected) > 0:
        wins = selected['Target'] == 1
        losses = selected['MAE_ATR'] <= -selected['SL_ATR']
        win_count = wins.sum()
        loss_count = losses.sum()
        
        if win_count + loss_count == 0:
            continue
            
        win_rate = win_count / (win_count + loss_count)
        pf = (selected.loc[wins, 'TP_ATR'].sum()) / (selected.loc[losses, 'SL_ATR'].sum() + 1e-9)
        print(f"Thresh {threshold:.2f} -> Trades: {win_count+loss_count:4d} | WR: {win_rate:05.2%} | PF: {pf:.2f}")


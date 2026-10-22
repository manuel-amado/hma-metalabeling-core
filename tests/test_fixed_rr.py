import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['Target'] = ((df['MFE_ATR'] >= 3.5) & (df['MAE_ATR'] > -4.0)).astype(int)
print(f"Dataset Target Dist: {df['Target'].mean():.2%}")

FEATURES = ['HMA_Slope', 'HMA_Accel', 'Candle_Vel', 'Candle_Dom', 'ZScore', 'Snapback', 
            'TimeInTrend', 'PainIndex', 'RSI', 'RSI_Slope', 'MTF_ATR', 'Dist_H4', 
            'Dist_200', 'Time_Sine', 'Time_Cosine', 'DayOfWeek', 'Spread_Ratio']

train_mask = (df['Time'].dt.year.isin([2022, 2023]))
test_mask = (df['Time'].dt.year == 2024)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

scaler = RobustScaler()
X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
X_test_sc = scaler.transform(df_test[FEATURES].values)

# Anti-Overfit Model
model = xgb.XGBClassifier(max_depth=3, learning_rate=0.05, n_estimators=100, random_state=42)
model.fit(X_train_sc, df_train['Target'].values)

probas = model.predict_proba(X_test_sc)[:, 1]
df_test['Proba'] = probas

print("--- OOS (2024) TP 3.5 / SL 4.0 Filtering ---")
for threshold in [0.20, 0.25, 0.30, 0.35]:
    selected = df_test[df_test['Proba'] >= threshold]
    if len(selected) > 0:
        # Note: If MFE hits 3.5 before MAE hits -4.0 it's a win.
        # If MAE hits -4.0 before MFE hits 3.5 it's a loss.
        # What if NEITHER hits?
        # We need to compute exact win/loss inside the selected
        wins = (selected['MFE_ATR'] >= 3.5) & (selected['MAE_ATR'] > -4.0)
        losses = selected['MAE_ATR'] <= -4.0
        win_count = wins.sum()
        loss_count = losses.sum()
        if (win_count + loss_count) == 0:
            continue
        win_rate = win_count / (win_count + loss_count)
        pf = (win_count * 3.5) / (loss_count * 4.0 + 1e-9)
        print(f"Thresh {threshold:.2f} -> Trades: {win_count+loss_count:4d} | WR: {win_rate:05.2%} | PF: {pf:.2f}")
    else:
        print(f"Thresh {threshold:.2f} -> Trades: 0")


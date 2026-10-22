import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import json
import math

# Load Data
df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

# Create Target: True Breakout
# A true breakout is one that hits 3 ATR in profit before hitting 1.5 ATR in loss.
df['Target'] = ((df['MFE_ATR'] >= 3.0) & (df['MAE_ATR'] > -1.5)).astype(int)

# Target Distribution
print(f"Target Distribution: {df['Target'].mean():.2%}")

# Features
FEATURES = ['HMA_Slope', 'HMA_Accel', 'Candle_Vel', 'Candle_Dom', 'ZScore', 'Snapback', 
            'TimeInTrend', 'PainIndex', 'RSI', 'RSI_Slope', 'MTF_ATR', 'Dist_H4', 
            'Dist_200', 'Time_Sine', 'Time_Cosine', 'DayOfWeek', 'Spread_Ratio']

# WFO Configuration
TEST_MONTHS = 12
train_years = [2022, 2023]
test_year = 2024

train_mask = (df['Time'].dt.year.isin(train_years))
test_mask = (df['Time'].dt.year == test_year)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

X_train = df_train[FEATURES].values
y_train = df_train['Target'].values

X_test = df_test[FEATURES].values
y_test = df_test['Target'].values

# Robust Scaler
scaler = RobustScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# Anti-Overfit Model (Shallow)
model = xgb.XGBClassifier(
    max_depth=3,
    learning_rate=0.05,
    n_estimators=150,
    objective='binary:logistic',
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train_sc, y_train)

# Evaluation
probas = model.predict_proba(X_test_sc)[:, 1]

print("\n--- OOS (2024) Evaluation ---")
for threshold in [0.30, 0.40, 0.50, 0.60]:
    mask = probas >= threshold
    selected = df_test[mask]
    if len(selected) > 0:
        win_rate = selected['Target'].mean()
        # Assume RR is 3.0 / 1.5 = 2.0
        pf = (win_rate * 3.0) / ((1 - win_rate) * 1.5 + 1e-9)
        print(f"Threshold {threshold:.2f} -> Trades: {len(selected):4d} | WR: {win_rate:05.2%} | Estimated PF: {pf:.2f}")
    else:
        print(f"Threshold {threshold:.2f} -> Trades: 0")


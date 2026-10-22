import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['Target'] = (df['Target_Bend_Ret'] > 0.05).astype(int)
df['Weight'] = np.abs(df['Target_Bend_Ret'])

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

model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
model.fit(X_train_sc, df_train['Target'].values, sample_weight=df_train['Weight'].values)

probas = model.predict_proba(X_test_sc)[:, 1]
df_test['Proba'] = probas

print("--- OOS (2024) Target_Bend_Ret ---")
for threshold in [0.45, 0.50, 0.55, 0.60, 0.65]:
    selected = df_test[df_test['Proba'] >= threshold]
    if len(selected) > 0:
        win_rate = (selected['Target_Bend_Ret'] > 0).mean()
        pf = selected[selected['Target_Bend_Ret'] > 0]['Target_Bend_Ret'].sum() / (abs(selected[selected['Target_Bend_Ret'] <= 0]['Target_Bend_Ret'].sum()) + 1e-9)
        print(f"Thresh {threshold:.2f} -> Trades: {len(selected):4d} | WR: {win_rate:05.2%} | PF: {pf:.2f}")
    else:
        print(f"Thresh {threshold:.2f} -> Trades: 0")


import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')
df['Target'] = (df['Target_Cross_Ret'] > 0.05).astype(int)

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

model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
model.fit(X_train_sc, df_train['Target'].values)

probas = model.predict_proba(X_test_sc)[:, 1]
df_test['Proba'] = probas

for threshold in [0.30, 0.35, 0.40]:
    selected = df_test[df_test['Proba'] >= threshold]
    print(f"Thresh {threshold:.2f} -> Total Crosses Above Threshold: {len(selected)}")


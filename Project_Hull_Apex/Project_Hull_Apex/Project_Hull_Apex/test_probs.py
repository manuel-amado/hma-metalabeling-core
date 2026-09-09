import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv('OmniApex_Dataset.csv')
features = ['Signal_Type', 'Micro_Velocity', 'Micro_Acceleration', 'Macro_Velocity', 'Tension_Ratio', 'ER_Kaufman', 'ADX_Value', 'RSI_Value']
X = df[features].astype(np.float32)
y = df['Target_Label'].astype(np.int64)
model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, random_state=42, use_label_encoder=False, eval_metric='logloss')
model.fit(X.values, y.values)
probs = model.predict_proba(X.values)[:, 1]
print(f'Max prob: {np.max(probs)}')
print(f'Min prob: {np.min(probs)}')
print(f'Mean prob: {np.mean(probs)}')
print(f'Trades with prob >= 0.65: {np.sum(probs >= 0.65)}')

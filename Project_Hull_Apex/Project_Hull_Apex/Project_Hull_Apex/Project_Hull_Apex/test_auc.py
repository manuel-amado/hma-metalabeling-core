import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score

df = pd.read_csv('OmniApex_Dataset.csv')
features = ['Signal_Type', 'Micro_Velocity', 'Micro_Acceleration', 'Macro_Velocity', 'Tension_Ratio', 'ER_Kaufman', 'ADX_Value', 'RSI_Value']
X = df[features].astype(np.float32)
y = df['Target_Label'].astype(np.int64)

model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, random_state=42, use_label_encoder=False, eval_metric='logloss')

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X.values, y.values, cv=cv, scoring='roc_auc')

print(f'Cross-Validated ROC AUC scores: {scores}')
print(f'Mean ROC AUC: {np.mean(scores)}')

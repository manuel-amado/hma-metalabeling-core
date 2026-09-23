import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score

df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/python/m2_metalabeling/models/XGBoost_Dataset_Final.csv')
df['Time'] = pd.to_datetime(df['Time'])
df = df[df['Signal_Dir'] == 1.0].copy().reset_index(drop=True)

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
split_date = pd.to_datetime('2023-01-01')

# === MODELO ACTUAL (sin explotar la autocorrelacion) ===
X = df[feature_cols]
y = df['Target']
train_mask = df['Time'] < split_date
X_train, X_test = X[train_mask], X[~train_mask]
y_train, y_test = y[train_mask], y[~train_mask]

m1 = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
m1.fit(X_train, y_train)
auc_current = roc_auc_score(y_test, m1.predict_proba(X_test)[:, 1])

# === MODELO MOMENTUM (explotando la autocorrelacion serial) ===
momentum_features = ['Keltner_Bandwidth_H4', 'ADX_Value_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1']
df2 = df.copy()
for feat in momentum_features:
    df2[feat + '_lag1'] = df2[feat].shift(1)

df2 = df2.dropna().reset_index(drop=True)

feature_cols_v2 = feature_cols + [f + '_lag1' for f in momentum_features]
X2 = df2[feature_cols_v2]
y2 = df2['Target']
train_mask2 = df2['Time'] < split_date

X2_train, X2_test = X2[train_mask2], X2[~train_mask2]
y2_train, y2_test = y2[train_mask2], y2[~train_mask2]

m2 = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
m2.fit(X2_train, y2_train)
proba_v2 = m2.predict_proba(X2_test)[:, 1]
auc_momentum = roc_auc_score(y2_test, proba_v2)

print('--- COMPARATIVA: Aprovechamos la autocorrelacion? ---')
print(f'Modelo Actual (sin momentum)   AUC OOS: {auc_current:.4f}')
print(f'Modelo v2 (con lag-1 momentum) AUC OOS: {auc_momentum:.4f}')
print(f'Mejora: {(auc_momentum - auc_current)*100:+.2f} pp')
print()

# Feature importance del modelo momentum
imp = pd.DataFrame({'Feature': feature_cols_v2, 'Importance': m2.feature_importances_}).sort_values('Importance', ascending=False)
print('--- IMPORTANCIA DE FEATURES EN MODELO MOMENTUM ---')
for _, row in imp.iterrows():
    tag = ' <- NUEVO MOMENTUM FEATURE' if 'lag1' in row['Feature'] else ''
    feat_name = row['Feature']
    importance = row['Importance']
    print(f'  {feat_name:<38} {importance:.4f}{tag}')

print()
# Comparar thresholds en el modelo momentum
print('--- OPTIMOS DE THRESHOLD EN MODELO MOMENTUM (IS puro) ---')
proba_all_v2 = m2.predict_proba(X2_train)[:, 1]
for t in [0.45, 0.50, 0.55, 0.60]:
    mask = proba_all_v2 >= t
    wr = y2_train[mask].mean() if mask.sum() > 0 else 0
    print(f'  Threshold {t:.2f} -> Trades: {mask.sum():<3} WR(IS): {wr:.1%}')

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('XGBoost_Dataset_Final.csv')
df['Time'] = pd.to_datetime(df['Time'])
feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

class PurgedWalkForwardCV:
    def __init__(self, n_splits=5, purge_days=7, embargo_days=5):
        self.n_splits = n_splits
        self.purge_days = pd.Timedelta(days=purge_days)
        self.embargo_days = pd.Timedelta(days=embargo_days)
        
    def split(self, df):
        n_samples = len(df)
        test_size = n_samples // (self.n_splits + 1)
        for i in range(1, self.n_splits + 1):
            train_end_idx = i * test_size
            test_end_idx = (i + 1) * test_size if i < self.n_splits else n_samples
            raw_train_idx = list(range(0, train_end_idx))
            raw_test_idx = list(range(train_end_idx, test_end_idx))
            test_start_time = df['Time'].iloc[raw_test_idx[0]]
            
            purge_cutoff = test_start_time - self.purge_days
            purged_train_idx = [idx for idx in raw_train_idx if df['Time'].iloc[idx] <= purge_cutoff]
            n_purged = len(raw_train_idx) - len(purged_train_idx)
            
            embargo_cutoff = test_start_time + self.embargo_days
            embargoed_test_idx = [idx for idx in raw_test_idx if df['Time'].iloc[idx] >= embargo_cutoff]
            n_embargoed = len(raw_test_idx) - len(embargoed_test_idx)
            
            yield purged_train_idx, embargoed_test_idx, n_purged, n_embargoed, test_start_time

cv = PurgedWalkForwardCV(n_splits=5, purge_days=7, embargo_days=5)
model = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss')

print('--- INSTITUTIONAL PURGED WALK-FORWARD MATRIX ---')
fold_auc = []
for fold, (train_idx, test_idx, n_purged, n_embargoed, test_start) in enumerate(cv.split(df), 1):
    X_train, y_train = df.iloc[train_idx][feature_cols], df.iloc[train_idx]['Target']
    X_test, y_test = df.iloc[test_idx][feature_cols], df.iloc[test_idx]['Target']
    
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    try:
        auc = roc_auc_score(y_test, y_prob)
    except Exception:
        auc = 0.5
        
    fold_auc.append(auc)
    print(f'[Fold {fold}] Cortando en: {test_start.date()}')
    print(f'   Trades Train: {len(train_idx)} | Trades Test: {len(test_idx)}')
    print(f'   [!] Purgados: {n_purged} trades (Target Leakage removido)')
    print(f'   [!] Embargados: {n_embargoed} trades (Serial Corr. removida)')
    print(f'   AUC Out-of-Sample: {auc:.3f}')
    print('-'*50)

mean_auc = np.mean(fold_auc)
print(f'\nAverage ROC AUC across Purged Folds: {mean_auc:.3f}')
if mean_auc >= 0.55:
    print('[+] MODELO APROBADO: El modelo M2 supera la barrera de validacion OOS institucional.')
else:
    print('[-] MODELO RECHAZADO: No supero el 0.55 OOS tras el Purging.')

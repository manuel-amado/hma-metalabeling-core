import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings('ignore')

dataset_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\portfolio\GBPJPY\XGBoost_Dataset_GBPJPY.csv'
df = pd.read_csv(dataset_path)
df['Time'] = pd.to_datetime(df['Time'])

# AMPUTACIÓN DEL RÉGIMEN TÓXICO PRE-2020
df_2020 = df[df['Time'] >= pd.to_datetime('2020-01-01')].copy().reset_index(drop=True)

print(f'=== AUDITORÍA AISLADA GBPJPY (RÉGIMEN 2020-2026) ===')
print(f'Trades totales (2020-2026): {len(df_2020)}')
print(f'Win Rate base del M1 (2020-2026): {df_2020.Target.mean():.2%}')

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4',
                'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

class TimeBasedRollingPurgedCV:
    def __init__(self, train_months=24, test_months=6, purge_days=7, embargo_days=5):
        self.train_offset = pd.DateOffset(months=train_months)
        self.test_offset = pd.DateOffset(months=test_months)
        self.purge_offset = pd.Timedelta(days=purge_days)
        self.embargo_offset = pd.Timedelta(days=embargo_days)

    def split(self, df, time_col='Time'):
        times = pd.to_datetime(df[time_col])
        start_date = times.min()
        end_date = times.max()
        current_train_start = start_date
        
        while True:
            current_train_end = current_train_start + self.train_offset
            current_test_start = current_train_end
            current_test_end = current_test_start + self.test_offset
            if current_test_start >= end_date: break
                
            purge_cut = current_train_end - self.purge_offset
            embargo_cut = current_test_start + self.embargo_offset
            
            train_mask = (times >= current_train_start) & (times <= purge_cut)
            test_mask = (times >= embargo_cut) & (times < current_test_end) & (times <= end_date)
            
            train_idx = df.index[train_mask].tolist()
            test_idx = df.index[test_mask].tolist()
            
            if len(train_idx) > 0 and len(test_idx) > 0:
                yield train_idx, test_idx, current_test_start.strftime('%Y-%m'), current_test_end.strftime('%Y-%m')
            
            current_train_start += self.test_offset

cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)

model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, 
                    subsample=0.8, colsample_bytree=0.8, random_state=42, 
                    eval_metric='logloss', base_score=0.5)

fold_aucs = []
fold = 1
for tr_idx, te_idx, test_start_str, test_end_str in cv.split(df_2020):
    Xtr = df_2020.iloc[tr_idx][feature_cols]
    ytr = df_2020.iloc[tr_idx]['Target']
    Xte = df_2020.iloc[te_idx][feature_cols]
    yte = df_2020.iloc[te_idx]['Target']
    
    if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
        fold += 1
        continue

    m = xgb.XGBClassifier(**model_params)
    m.fit(Xtr, ytr)
    auc = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
    fold_aucs.append(auc)
    print(f'[Fold {fold:<2}] OOS: {test_start_str} to {test_end_str} | Train: {len(Xtr):<3} | Test: {len(Xte):<2} | AUC: {auc:.3f}')
    fold += 1

mean_auc = np.mean(fold_aucs) if fold_aucs else 0
print(f'\n[VEREDICTO RISK MANAGER] AUC Medio OOS (2020-2026): {mean_auc:.3f}')

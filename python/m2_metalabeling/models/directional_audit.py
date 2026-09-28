import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import m2cgen as m2c
import re
import os
import glob
import shutil
import warnings
warnings.filterwarnings('ignore')

# 1. Configuración de Rutas
files_dir = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files'
base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'
mql_experts_dir = os.path.join(base_dir, 'mql5', 'Experts', 'HMA_SQX_Discovery')
mql_include_dir = os.path.join(base_dir, 'mql5', 'Include')
portfolio_dir = os.path.join(base_dir, 'portfolio')

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
                yield train_idx, test_idx
            
            current_train_start += self.test_offset

def evaluate_direction(df_subset, direction_name):
    if len(df_subset) < 40:
        return 0.0, 0
    
    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)
    model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
                        
    fold_aucs = []
    for tr_idx, te_idx in cv.split(df_subset):
        Xtr, ytr = df_subset.iloc[tr_idx][feature_cols], df_subset.iloc[tr_idx]['Target']
        Xte, yte = df_subset.iloc[te_idx][feature_cols], df_subset.iloc[te_idx]['Target']
        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2: continue
            
        m = xgb.XGBClassifier(**model_params)
        m.fit(Xtr, ytr)
        auc = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
        fold_aucs.append(auc)
        
    return np.mean(fold_aucs) if fold_aucs else 0.0, len(df_subset)

def process_asset(symbol):
    f_path = os.path.join(files_dir, f'XGBoost_Features_M1_{symbol}.csv')
    d_path = os.path.join(files_dir, f'Pipeline_Extractor_M1_{symbol}.csv')
    
    if not os.path.exists(f_path) or not os.path.exists(d_path): return
        
    features = pd.read_csv(f_path)
    if features.empty: return
    features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))
    
    deal_rows = []
    with open(d_path, 'r', encoding='utf-16') as f:
        for line in f.readlines():
            parts = line.strip().split(';')
            if len(parts) >= 14 and parts[8] == 'out':
                try: deal_rows.append({'PositionId': int(parts[1]), 'Profit': float(parts[12])})
                except: pass
                
    deals = pd.DataFrame(deal_rows)
    if deals.empty: return
        
    df = pd.merge(features, deals, left_on='Ticket', right_on='PositionId', how='inner')
    df = df.sort_values('Time').reset_index(drop=True)
    df['Target'] = (df['Profit'] > 0).astype(int)
    
    df_2020 = df[df['Time'] >= pd.to_datetime('2020-01-01')].copy().reset_index(drop=True)
    
    df_long = df_2020[df_2020['Signal_Dir'] == 1.0].copy().reset_index(drop=True)
    df_short = df_2020[df_2020['Signal_Dir'] == -1.0].copy().reset_index(drop=True)
    
    auc_long, trades_long = evaluate_direction(df_long, 'LONG')
    auc_short, trades_short = evaluate_direction(df_short, 'SHORT')
    
    print(f"{symbol:<8} | LONGS: {auc_long:.3f} ({trades_long:<3} tr) | SHORTS: {auc_short:.3f} ({trades_short:<3} tr)")

symbols = set()
for f in glob.glob(os.path.join(files_dir, 'Pipeline_Extractor_M1_*.csv')):
    sym = os.path.basename(f).replace('Pipeline_Extractor_M1_', '').replace('.csv', '')
    symbols.add(sym)

print("\n--- MATRIZ DIRECCIONAL AUC (2020-2026) ---")
for s in sorted(list(symbols)): process_asset(s)
print("------------------------------------------\n")

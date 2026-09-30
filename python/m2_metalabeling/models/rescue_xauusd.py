import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import os
import warnings
warnings.filterwarnings('ignore')

# CV Institucional
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

# Rescue Operation
files_dir = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files'
f_path = os.path.join(files_dir, 'XGBoost_Features_M1_XAUUSD.csv')
d_path = os.path.join(files_dir, 'Pipeline_Extractor_M1_XAUUSD.csv')

if not os.path.exists(f_path) or not os.path.exists(d_path):
    print("ERROR: No se encontraron los archivos CSV. El usuario debe ejecutar la extraccion primero.")
else:
    features = pd.read_csv(f_path)
    features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))
    
    deal_rows = []
    with open(d_path, 'r', encoding='utf-16') as f:
        for line in f.readlines():
            parts = line.strip().split(';')
            if len(parts) >= 14 and parts[8] == 'out':
                try: deal_rows.append({'PositionId': int(parts[1]), 'Profit': float(parts[12])})
                except: pass
                
    deals = pd.DataFrame(deal_rows)
    df = pd.merge(features, deals, left_on='Ticket', right_on='PositionId', how='inner')
    df = df.sort_values('Time').reset_index(drop=True)
    df['Target'] = (df['Profit'] > 0).astype(int)
    
    # 2020-2026 
    df_eval = df[(df['Time'] >= pd.to_datetime('2020-01-01'))].copy().reset_index(drop=True)
    
    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)
    model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
    
    feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
    
    fold_aucs = []
    for tr_idx, te_idx in cv.split(df_eval):
        Xtr, ytr = df_eval.iloc[tr_idx][feature_cols], df_eval.iloc[tr_idx]['Target']
        Xte, yte = df_eval.iloc[te_idx][feature_cols], df_eval.iloc[te_idx]['Target']
        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2: continue
        
        m = xgb.XGBClassifier(**model_params)
        m.fit(Xtr, ytr)
        auc = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
        fold_aucs.append(auc)
        
    mean_auc = np.mean(fold_aucs) if fold_aucs else 0.0
    print(f"=== OPERACION RESCATE XAUUSD ===")
    print(f"Trades Evaluados (2020-2026): {len(df_eval)}")
    print(f"AUC OOS Promedio: {mean_auc:.4f}")
    if mean_auc >= 0.52:
        print("VEREDICTO: APROBADO. Edge recuperado con exito.")
    else:
        print("VEREDICTO: VETADO. El ruido no era el problema, el chasis no sirve para el oro.")

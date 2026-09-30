import pandas as pd
import numpy as np
import xgboost as xgb
import os
import warnings
warnings.filterwarnings('ignore')

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
                yield current_test_start, current_test_end, train_idx, test_idx
            
            current_train_start += self.test_offset

files_dir = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files'
f_path = os.path.join(files_dir, 'XGBoost_Features_M1_GBPUSD.csv')
d_path = os.path.join(files_dir, 'Pipeline_Extractor_M1_GBPUSD.csv')

if not os.path.exists(f_path) or not os.path.exists(d_path):
    print("ERROR: CSVs no encontrados.")
else:
    # 1. Leer Features
    features = pd.read_csv(f_path)
    features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))
    
    # 2. Leer Deals (Beneficios Asimetricos)
    deal_rows = []
    with open(d_path, 'r', encoding='utf-16') as f:
        for line in f.readlines():
            parts = line.strip().split(';')
            if len(parts) >= 14 and parts[8] == 'out':
                try: deal_rows.append({'PositionId': int(parts[1]), 'Profit': float(parts[12])})
                except: pass
                
    deals = pd.DataFrame(deal_rows)
    
    # 3. Mergear
    df = pd.merge(features, deals, left_on='Ticket', right_on='PositionId', how='inner')
    df = df.sort_values('Time').reset_index(drop=True)
    df['Target'] = (df['Profit'] > 0).astype(int)
    
    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6)
    feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
    model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
    
    oos_trades = []
    
    for t_start, t_end, tr_idx, te_idx in cv.split(df):
        Xtr = df.iloc[tr_idx][feature_cols]
        ytr = df.iloc[tr_idx]['Target']
        
        if len(np.unique(ytr)) < 2: continue
            
        m = xgb.XGBClassifier(**model_params)
        m.fit(Xtr, ytr)
        
        Xte = df.iloc[te_idx]
        probs = m.predict_proba(Xte[feature_cols])[:, 1]
        
        accepted = Xte.copy()
        accepted['Prob'] = probs
        accepted = accepted[accepted['Prob'] >= 0.50]
        
        oos_trades.append(accepted)
        
    if len(oos_trades) > 0:
        master_oos = pd.concat(oos_trades).drop_duplicates(subset=['Ticket']).sort_values('Time')
        master_oos['Cumulative_Profit'] = master_oos['Profit'].cumsum()
        
        print('=== VEREDICTO ASIMETRICO: BACKTEST OOS (2017-2026) ===')
        wins = master_oos['Target'].sum()
        total = len(master_oos)
        wr = wins / total if total > 0 else 0
        
        gross_p = master_oos[master_oos['Profit'] > 0]['Profit'].sum()
        gross_l = abs(master_oos[master_oos['Profit'] < 0]['Profit'].sum())
        pf = gross_p / gross_l if gross_l > 0 else 99.99
        
        print(f'Total Trades OOS: {total}')
        print(f'Win Rate: {wr:.2%}')
        print(f'Profit Factor: {pf:.2f}')
        print(f'Net Profit: ${master_oos.Profit.sum():.2f}')
        
        print('\n-- Desglose Anual OOS --')
        master_oos['Year'] = master_oos['Time'].dt.year
        for year in sorted(master_oos['Year'].unique()):
            y_df = master_oos[master_oos['Year'] == year]
            y_wins = y_df['Target'].sum()
            y_wr = y_wins / len(y_df) if len(y_df)>0 else 0
            y_gp = y_df[y_df['Profit'] > 0]['Profit'].sum()
            y_gl = abs(y_df[y_df['Profit'] < 0]['Profit'].sum())
            y_pf = y_gp / y_gl if y_gl > 0 else 99.99
            print(f'Año {year}: {len(y_df):<3} trades | WR: {y_wr:>3.0%} | PF: {y_pf:>5.2f} | Profit: ${y_df.Profit.sum():>8.2f}')
    else:
        print('Ningun trade supero el umbral OOS.')

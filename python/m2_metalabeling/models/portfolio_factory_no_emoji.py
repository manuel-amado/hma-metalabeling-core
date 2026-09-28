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

def process_asset(symbol):
    print(f'\n' + '='*50)
    print(f'[ PROCESANDO ACTIVO: {symbol} ]')
    print('='*50)
    
    f_path = os.path.join(files_dir, f'XGBoost_Features_M1_{symbol}.csv')
    d_path = os.path.join(files_dir, f'Pipeline_Extractor_M1_{symbol}.csv')
    
    if not os.path.exists(f_path) or not os.path.exists(d_path):
        print(f'[SKIPPED] Faltan archivos para {symbol}')
        return
        
    features = pd.read_csv(f_path)
    if features.empty:
        print(f'[SKIPPED] Features vacio para {symbol}')
        return
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
    
    print(f'Trades Extraidos (2015-2026): {len(df)}')
    
    df_2020 = df[df['Time'] >= pd.to_datetime('2020-01-01')].copy().reset_index(drop=True)
    print(f'Trades Aislados (2020-2026): {len(df_2020)}')
    if len(df_2020) < 50:
        print(f'[VETO] Datos insuficientes post-2020 para {symbol}')
        return
        
    print(f'Win Rate M1 (2020-2026): {df_2020.Target.mean():.2%}')
    
    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)
    model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
                        
    fold_aucs = []
    for tr_idx, te_idx in cv.split(df_2020):
        Xtr, ytr = df_2020.iloc[tr_idx][feature_cols], df_2020.iloc[tr_idx]['Target']
        Xte, yte = df_2020.iloc[te_idx][feature_cols], df_2020.iloc[te_idx]['Target']
        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2: continue
            
        m = xgb.XGBClassifier(**model_params)
        m.fit(Xtr, ytr)
        auc = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
        fold_aucs.append(auc)
        
    mean_auc = np.mean(fold_aucs) if fold_aucs else 0.0
    print(f'[AUDITORIA OOS] AUC Medio (2020-2026): {mean_auc:.3f}')
    
    if mean_auc < 0.52:
        print(f'[VETO MANTENIDO] La IA no detecta Edge estadistico sobre {symbol}. Abortando despliegue.')
        return
        
    print(f'[APROBADO] Edge validado matematicamente para {symbol}. Empaquetando Produccion...')
    
    asset_dir = os.path.join(portfolio_dir, symbol)
    os.makedirs(asset_dir, exist_ok=True)
    df.to_csv(os.path.join(asset_dir, f'XGBoost_Dataset_{symbol}.csv'), index=False)
    
    df_prod = df[df['Time'] >= pd.to_datetime('2024-01-01')].copy().reset_index(drop=True)
    m_final = xgb.XGBClassifier(**model_params)
    m_final.fit(df_prod[feature_cols], df_prod['Target'])
    
    c_code = m2c.export_to_c(m_final)
    c_code = re.sub(r'#include <math\.h>\s*', '', c_code)
    c_code = re.sub(r'#include <string\.h>\s*', '', c_code)
    c_code = re.sub(r'^.*?void score', 'void GetXGBoostProbability', c_code, flags=re.DOTALL)
    mql5_code = c_code.replace('(double * input, double * output) {', '(const double &features[], double &result[]) {')
    mql5_code = mql5_code.replace('input[', 'features[')
    mql5_code = mql5_code.replace('output[', 'result[')
    mql5_code = mql5_code.replace('exp(', 'MathExp(')
    mql5_code = re.sub(r'memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;', r'result[0] = \1;\n    result[1] = \2;', mql5_code)
    
    mql5_final = f"//+------------------------------------------------------------------+\n" \
                 f"//| M2_XGBoost_Oracle_{symbol}.mqh |\n" \
                 f"//| REGIMEN: Rolling Window 2024-2026 (Alta Volatilidad + ADX > 25) |\n" \
                 f"//+------------------------------------------------------------------+\n" \
                 f"double MathExpSafe(double x) {{ if (x > 100) return MathExp(100); if (x < -100) return MathExp(-100); return MathExp(x); }}\n" \
                 f"double sigmoid(double x) {{\n" \
                 f"    if (x < 0.0) {{ double z = MathExpSafe(x); return z / (1.0 + z); }}\n" \
                 f"    return 1.0 / (1.0 + MathExpSafe(-x));\n" \
                 f"}}\n{mql5_code}"
                 
    oracle_path = os.path.join(asset_dir, f'M2_XGBoost_Oracle_{symbol}.mqh')
    with open(oracle_path, 'w', encoding='utf-8') as f: f.write(mql5_final)
    shutil.copy(oracle_path, os.path.join(mql_include_dir, f'M2_XGBoost_Oracle_{symbol}.mqh'))
    
    ea_src = os.path.join(mql_experts_dir, 'Strategy 2.91.69.mq5')
    ea_dest = os.path.join(asset_dir, f'Strategy_{symbol}_Production.mq5')
    with open(ea_src, 'r', encoding='utf-8', errors='ignore') as f: ea_code = f.read()
    ea_code = re.sub(r'#include\s*[\"<]M2_XGBoost_Oracle(?:_[A-Z]+)?\.mqh[\">]', f'#include "M2_XGBoost_Oracle_{symbol}.mqh"', ea_code)
    ea_code = re.sub(r'input\s+bool\s+TradeShorts\s*=\s*false;\s*', 'input bool TradeShorts = true; ', ea_code)
    with open(ea_dest, 'w', encoding='utf-8') as f: f.write(ea_code)
    shutil.copy(ea_dest, os.path.join(mql_experts_dir, f'Strategy_{symbol}_Production.mq5'))
    
    print(f'[VAULT] Activo {symbol} securizado en Boveda.')

symbols = set()
for f in glob.glob(os.path.join(files_dir, 'Pipeline_Extractor_M1_*.csv')):
    sym = os.path.basename(f).replace('Pipeline_Extractor_M1_', '').replace('.csv', '')
    symbols.add(sym)

for s in sorted(list(symbols)): process_asset(s)
print('\n*** PIPELINE GLOBAL FINALIZADO ***')

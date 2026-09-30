import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import m2cgen as m2c
import re
import os
import shutil

# Rutas Centrales
features_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XGBoost_Features_M1.csv'
deals_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Pipeline_Extractor_M1.csv'

base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'
portfolio_dir = os.path.join(base_dir, 'portfolio', 'GBPJPY')
os.makedirs(portfolio_dir, exist_ok=True)

# 1. Cargar Features
features = pd.read_csv(features_path)
features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))

# 2. Cargar Deals (Soporta Longs y Shorts)
deal_rows = []
with open(deals_path, 'r', encoding='utf-16') as f:
    for line in f.readlines():
        parts = line.strip().split(';')
        if len(parts) >= 14 and parts[8] == 'out': # Detecta cualquier cierre
            try:
                position_id = int(parts[1])
                profit = float(parts[12])
                deal_rows.append({'PositionId': position_id, 'Profit': profit})
            except: pass

deals = pd.DataFrame(deal_rows)

# 3. Merge Estricto
df = pd.merge(features, deals, left_on='Ticket', right_on='PositionId', how='inner')
df = df.sort_values('Time').reset_index(drop=True)
df['Target'] = (df['Profit'] > 0).astype(int)

# ARCHIVAR DATASET
dataset_vault = os.path.join(portfolio_dir, 'XGBoost_Dataset_GBPJPY.csv')
df.to_csv(dataset_vault, index=False)

# 4. Análisis Institucional Histórico (Rolling Window 2015-2026)
print(f'=== BACKTEST INSTITUCIONAL GBPJPY: PURGED ROLLING WALK-FORWARD ===')
print(f'Trades totales (GBPJPY): {len(df)}')
print(f'Win Rate base histórico: {df.Target.mean():.2%}')

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

print('\n--- Deslizamiento OOS ---')
fold_aucs = []
fold = 1
for tr_idx, te_idx, test_start_str, test_end_str in cv.split(df):
    Xtr = df.iloc[tr_idx][feature_cols]
    ytr = df.iloc[tr_idx]['Target']
    Xte = df.iloc[te_idx][feature_cols]
    yte = df.iloc[te_idx]['Target']
    
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
print(f'\n[RESULTADO GLOBAL GBPJPY] AUC Medio OOS: {mean_auc:.3f}')

# 5. Generar Oráculo de Producción (2024-2026)
df_window = df[df['Time'] >= pd.to_datetime('2024-01-01')].copy().reset_index(drop=True)
X_full = df_window[feature_cols]
y_full = df_window['Target']

final_model = xgb.XGBClassifier(**model_params)
final_model.fit(X_full, y_full)

c_code = m2c.export_to_c(final_model)
c_code = re.sub(r'#include <math\.h>\s*', '', c_code)
c_code = re.sub(r'#include <string\.h>\s*', '', c_code)
c_code = re.sub(r'^.*?void score', 'void GetXGBoostProbability', c_code, flags=re.DOTALL)
mql5_code = c_code.replace('(double * input, double * output) {', '(const double &features[], double &result[]) {')
mql5_code = mql5_code.replace('input[', 'features[')
mql5_code = mql5_code.replace('output[', 'result[')
mql5_code = mql5_code.replace('exp(', 'MathExp(')
mql5_code = re.sub(r'memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;', r'result[0] = \1;\n    result[1] = \2;', mql5_code)

mql5_header = """//+------------------------------------------------------------------+
//|                                     M2_XGBoost_Oracle_GBPJPY.mqh |
//| REGIMEN: Rolling Window 2024-2026 (Alta Volatilidad + ADX > 25) |
//| Generado por la Fabrica de Modelos Antigravity                   |
//+------------------------------------------------------------------+
#property copyright "Antigravity Quant AI"

double sigmoid(double x) {
    if (x < 0.0) {
        double z = MathExp(x);
        return z / (1.0 + z);
    }
    return 1.0 / (1.0 + MathExp(-x));
}
"""
mql5_final = mql5_header + mql5_code

# Guardar en Vault de GBPJPY
oracle_vault = os.path.join(portfolio_dir, 'M2_XGBoost_Oracle_GBPJPY.mqh')
with open(oracle_vault, 'w', encoding='utf-8') as f:
    f.write(mql5_final)

# Copiar a MQL5 Include para compilación
mql_include_dir = os.path.join(base_dir, 'mql5', 'Include')
oracle_include = os.path.join(mql_include_dir, 'M2_XGBoost_Oracle_GBPJPY.mqh')
shutil.copy(oracle_vault, oracle_include)

# 6. Crear EA de Producción para GBPJPY
mql_experts_dir = os.path.join(base_dir, 'mql5', 'Experts', 'HMA_SQX_Discovery')
ea_src = os.path.join(mql_experts_dir, 'Strategy 2.91.69.mq5')
ea_gbpjpy = os.path.join(mql_experts_dir, 'Strategy_GBPJPY_Production.mq5')

with open(ea_src, 'r', encoding='utf-8', errors='ignore') as f:
    ea_code = f.read()

# Apuntar al Oráculo de GBPJPY
ea_code = re.sub(
    r'#include\s*[\"<]M2_XGBoost_Oracle(?:_XAUUSD)?\.mqh[\">]',
    '#include "M2_XGBoost_Oracle_GBPJPY.mqh"',
    ea_code
)
# Habilitar los Shorts por defecto para el EA de Producción de GBPJPY
ea_code = re.sub(
    r'input\s+bool\s+TradeShorts\s*=\s*false;\s*',
    'input bool TradeShorts = true; ',
    ea_code
)

with open(ea_gbpjpy, 'w', encoding='utf-8') as f:
    f.write(ea_code)

# Copiar EA a Vault
ea_vault = os.path.join(portfolio_dir, 'Strategy_GBPJPY_Production.mq5')
shutil.copy(ea_gbpjpy, ea_vault)

print(f'\n[VAULT] Oráculo y EA de Producción empaquetados en: {portfolio_dir}')

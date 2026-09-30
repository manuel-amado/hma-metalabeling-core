import pandas as pd
import numpy as np
import xgboost as xgb
import m2cgen as m2c
import re

features_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XGBoost_Features_M1.csv'
deals_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Pipeline_Extractor_M1.csv'

features = pd.read_csv(features_path)
features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))

deal_rows = []
with open(deals_path, 'r', encoding='utf-16') as f:
    for line in f.readlines():
        parts = line.strip().split(';')
        if len(parts) >= 14 and parts[8] == 'out' and parts[7] == 'sell':
            try:
                position_id = int(parts[1])
                profit = float(parts[12])
                deal_rows.append({'PositionId': position_id, 'Profit': profit})
            except: pass

deals = pd.DataFrame(deal_rows)

df = pd.merge(features[features['Signal_Dir'] == 1.0], deals, left_on='Ticket', right_on='PositionId', how='inner')
df = df.sort_values('Time').reset_index(drop=True)
df['Target'] = (df['Profit'] > 0).astype(int)

WINDOW_START = '2024-01-01'
df_window = df[df['Time'] >= pd.to_datetime(WINDOW_START)].copy().reset_index(drop=True)

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4',
                'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05,
                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                    eval_metric='logloss', base_score=0.5)

X_full = df_window[feature_cols]
y_full = df_window['Target']

final_model = xgb.XGBClassifier(**model_params)
final_model.fit(X_full, y_full)

c_code = m2c.export_to_c(final_model)
c_code = re.sub(r'#include <math\.h>\s*', '', c_code)
c_code = re.sub(r'#include <string\.h>\s*', '', c_code)
c_code = re.sub(r'^.*?void score', 'void GetXGBoostProbability', c_code, flags=re.DOTALL)

mql5_code = c_code.replace('(double * input, double * output) {',
                            '(const double &features[], double &result[]) {')
mql5_code = mql5_code.replace('input[', 'features[')
mql5_code = mql5_code.replace('output[', 'result[')
mql5_code = mql5_code.replace('exp(', 'MathExp(')

mql5_code = re.sub(
    r'memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;',
    r'result[0] = \1;\n    result[1] = \2;',
    mql5_code
)

mql5_header = """//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
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

paths = [
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\M2_XGBoost_Oracle.mqh',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Include\M2_XGBoost_Oracle.mqh'
]
for p in paths:
    try:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(mql5_final)
    except:
        pass

print('M2_XGBoost_Oracle.mqh exportado limpiamente con los datos de la Fabrica.')

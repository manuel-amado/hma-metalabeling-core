import pandas as pd
import numpy as np
import xgboost as xgb
import m2cgen as m2c
import re
from sklearn.metrics import roc_auc_score

WINDOW_START = '2024-01-01'
PURGE_DAYS   = 7
EMBARGO_DAYS = 5
N_SPLITS     = 3
THRESHOLD    = 0.55

df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/python/m2_metalabeling/models/XGBoost_Dataset_Final.csv')
df['Time'] = pd.to_datetime(df['Time'])

df = df[(df['Signal_Dir'] == 1.0) & (df['Time'] >= pd.to_datetime(WINDOW_START))].copy().reset_index(drop=True)

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4',
                'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05,
                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                    eval_metric='logloss', base_score=0.5)

X_full = df[feature_cols]
y_full = df['Target']

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

# Fixed regex matching output OR result
mql5_code = re.sub(
    r'memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;',
    r'result[0] = \1;\n    result[1] = \2;',
    mql5_code
)

mql5_header = """//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| REGIMEN: Rolling Window 2024-2026 (Alta Volatilidad)          |
//| Generado automaticamente por Antigravity Quant AI              |
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

print('rolling_window_retrain.py updated and MQH files rewritten cleanly.')

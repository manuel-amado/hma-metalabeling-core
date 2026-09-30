import pandas as pd
import numpy as np
import xgboost as xgb
import m2cgen as m2c

df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/python/m2_metalabeling/models/XGBoost_Dataset_Final.csv')
df = df[df['Signal_Dir'] == 1.0].copy()

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
X = df[feature_cols]
y = df['Target']

model = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss', base_score=0.5)
model.fit(X, y)

c_code = m2c.export_to_c(model)
mql5_code = c_code.replace('void score(double * input, double * output) {', 'void GetXGBoostProbability(const double &features[], double &result[]) {')
mql5_code = mql5_code.replace('input[', 'features[')
mql5_code = mql5_code.replace('output[', 'result[')

mql5_header = """//+------------------------------------------------------------------+
//|                                         M2_XGBoost_Oracle.mqh |
//| Generated automatically by m2cgen for MetaTrader 5            |
//| Model: XGBoost (Longs Only Specialized)                       |
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

for p in [r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\M2_XGBoost_Oracle.mqh', r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Include\M2_XGBoost_Oracle.mqh']:
    try:
        with open(p, 'w') as f:
            f.write(mql5_final)
    except:
        pass
print('OK - Retrained and Exported')

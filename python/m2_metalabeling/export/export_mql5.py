import pandas as pd
import xgboost as xgb
import m2cgen as m2c
import re

# Load dataset and retrain model to get the exact state
df = pd.read_csv("XGBoost_Dataset_Final.csv")
feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
X = df[feature_cols]
y = df['Target']

split_idx = int(len(df) * 0.7)
X_train = X.iloc[:split_idx]
y_train = y.iloc[:split_idx]

model = xgb.XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, random_state=42, 
    base_score=0.5, eval_metric='logloss'
)
model.fit(X_train, y_train)

print("Exporting XGBoost to C code via m2cgen...")
c_code = m2c.export_to_c(model)

# Convert C syntax to MQL5 syntax
mql5_code = "//+------------------------------------------------------------------+\n"
mql5_code += "//|                                         M2_XGBoost_Oracle.mqh |\n"
mql5_code += "//| Generated automatically by m2cgen for MetaTrader 5            |\n"
mql5_code += "//+------------------------------------------------------------------+\n"
mql5_code += "#property copyright \"Antigravity Quant AI\"\n\n"

# Remove the math.h and string.h includes
c_code = re.sub(r'#include <math\.h>', '', c_code)
c_code = re.sub(r'#include <string\.h>', '', c_code)

# Replace the C function signature with MQL5 arrays
c_code = c_code.replace("void score(double * input, double * output)", "void GetXGBoostProbability(const double &input[], double &output[])")

# Replace C's exp() with MathExp() just in case (MQL5 supports both, but MathExp is native)
c_code = c_code.replace(" exp(", " MathExp(")

mql5_code += c_code

with open(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Include\M2_XGBoost_Oracle.mqh", "w") as f:
    f.write(mql5_code)

print("Successfully generated M2_XGBoost_Oracle.mqh in MT5 Include folder.")

import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import json
import math

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing"
MODELS_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\Alpha_Sniper_Normal\Models"
csv_path = f"{DATA_DIR}\Alpha_Omni_Dataset_XAUUSD.csv"

df = pd.read_csv(csv_path)
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['Target'] = ((df['MFE_ATR'] >= 3.5) & (df['MAE_ATR'] > -4.0)).astype(int)

FEATURES = ['HMA_Slope', 'HMA_Accel', 'Candle_Vel', 'Candle_Dom', 'ZScore', 'Snapback', 
            'TimeInTrend', 'PainIndex', 'RSI', 'RSI_Slope', 'MTF_ATR', 'Dist_H4', 
            'Dist_200', 'Time_Sine', 'Time_Cosine', 'DayOfWeek', 'Spread_Ratio']

TRAIN_YEARS = 2
TEST_MONTHS = 12

def parse_tree_recursive(lines_dict, node_id, indent="    "):
    line = lines_dict[node_id]
    if 'leaf' in line:
        val = line.split('leaf=')[1]
        return f"{indent}sum += {float(val):.9f};\n"
    else:
        condition = line.split('[f')[1].split(']')[0]
        feat_idx = int(condition.split('<')[0])
        thresh = float(condition.split('<')[1])
        
        yes_node = line.split('yes=')[1].split(',')[0]
        no_node = line.split('no=')[1].split(',')[0]
        
        c = f"{indent}if(scaled[{feat_idx}] < {thresh}) {{\n"
        c += parse_tree_recursive(lines_dict, yes_node, indent + "    ")
        c += f"{indent}}} else {{\n"
        c += parse_tree_recursive(lines_dict, no_node, indent + "    ")
        c += f"{indent}}}\n"
        return c

def generate_mqh(df, symbol):
    code = f"//+------------------------------------------------------------------+\n"
    code += f"//| XGBoost Model WFO OMNI - {symbol} \n"
    code += f"//+------------------------------------------------------------------+\n"
    code += f"// Target: TP 3.5 ATR / SL 4.0 ATR\n"
    
    routing_code = f"double XGBoost_Predict_WFO_OMNI_{symbol}(double &features[], int current_year, int current_month) {{\n"

    for test_year in range(2018, 2027):
        for test_month in [1, 13]: # Only once a year for this test to speed up, or maybe every 6 months? Let's just do yearly.
            if test_month > 12: continue
            
            start_train_year = test_year - TRAIN_YEARS
            
            train_mask = (df['Time'].dt.year >= start_train_year) & (df['Time'].dt.year < test_year)
            df_train = df[train_mask]
            if len(df_train) < 50: continue
            
            X_train = df_train[FEATURES].values
            y_train = df_train['Target'].values
            
            scaler = RobustScaler()
            X_train_sc = scaler.fit_transform(X_train)
            
            model = xgb.XGBClassifier(max_depth=3, learning_rate=0.05, n_estimators=100, random_state=42)
            model.fit(X_train_sc, y_train)
            
            func_name = f"predict_OMNI_{symbol}_{test_year}_{test_month}"
            
            code += f"double {func_name}(double &f[]) {{\n"
            code += f"    double scaled[{len(FEATURES)}];\n"
            for i in range(len(FEATURES)):
                code += f"    scaled[{i}] = (f[{i}] - ({scaler.center_[i]:.5f})) / ({scaler.scale_[i]:.5f});\n"
            
            code += f"    double sum = 0.0;\n"
            
            booster = model.get_booster()
            trees = booster.get_dump()
            
            for tree_idx, tree_str in enumerate(trees):
                lines = tree_str.strip().split('\n')
                lines_dict = {}
                for line in lines:
                    node_id = line.split(':')[0].strip()
                    lines_dict[node_id] = line
                
                code += parse_tree_recursive(lines_dict, '0', "    ")
                
            bs_str = json.loads(booster.save_config())['learner']['learner_model_param']['base_score']
            bs_val = float(bs_str[0]) if isinstance(bs_str, list) else float(bs_str.strip('[]'))
            margin = 0.0 if bs_val == 0.5 else -math.log(1.0 / bs_val - 1.0)
            
            code += f"    return 1.0 / (1.0 + MathExp(-(sum + ({margin}))));\n}}\n\n"
            
            routing_code += f"    if(current_year == {test_year}) return {func_name}(features);\n"
            print(f"[{symbol} - {test_year}] OMNI Trained.")

    routing_code += f"    return {func_name}(features); // Fallback\n}}\n"
    
    with open(os.path.join(MODELS_DIR, f"XGBoost_Model_WFO_OMNI_{symbol}.mqh"), "w") as f:
        f.write(code + routing_code)
    print(f"[{symbol}] Modulo OMNI guardado.")

print("--- OMNI Dynamic WFO ---")
generate_mqh(df, "XAUUSD")

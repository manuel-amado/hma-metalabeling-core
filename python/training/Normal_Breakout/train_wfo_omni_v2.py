import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import json
import math

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing"
MODELS_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\Alpha_Sniper_Normal\Models"
csv_path = f"{DATA_DIR}\Alpha_Omni_V3_Dataset_XAUUSD.csv"

df = pd.read_csv(csv_path)
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

# We train the AI to predict pure directional truth (does the wave make money before it reverses?)
df['Target'] = (df['Target_Cross_Ret'] > 0.05).astype(int)

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

TRAIN_YEARS = 2

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
    code += f"//| XGBoost Model WFO OMNI V2 - {symbol} \n"
    code += f"//+------------------------------------------------------------------+\n"
    
    routing_code = f"double XGBoost_Predict_WFO_OMNI_V2_{symbol}(double &features[], int current_year, int current_month) {{\n"

    for test_year in range(2018, 2027):
        start_train_year = test_year - TRAIN_YEARS
        
        train_mask = (df['Time'].dt.year >= start_train_year) & (df['Time'].dt.year < test_year)
        df_train = df[train_mask]
        if len(df_train) < 50: continue
        
        X_train = df_train[FEATURES].values
        y_train = df_train['Target'].values
        
        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train)
        
        # Deep enough to understand the Ribbon combinations, but shallow enough to prevent overfit
        model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
        model.fit(X_train_sc, y_train)
        
        func_name = f"predict_OMNI_V2_{symbol}_{test_year}"
        
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
        print(f"[{symbol} - {test_year}] OMNI V2 Trained.")

    routing_code += f"    return {func_name}(features); // Fallback\n}}\n"
    
    with open(os.path.join(MODELS_DIR, f"XGBoost_Model_WFO_OMNI_V2_{symbol}.mqh"), "w") as f:
        f.write(code + routing_code)
    print(f"[{symbol}] Modulo OMNI V2 guardado.")

generate_mqh(df, "XAUUSD")

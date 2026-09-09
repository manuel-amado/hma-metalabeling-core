import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import math
import json
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODELS_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Models"
SYMBOLS = ["XAUUSD"] # Start with XAUUSD for V20

FEATURES = [
    "CrossDir", "HMA_Slope", "HMA_Accel", "Candle_Vel", 
    "Time_in_Trend", "Snapback_Dist", "RSI", 
    "Time_Sine", "Time_Cosine", "PainIndex"
]

TRAIN_MONTHS = 24
TEST_MONTHS = 6

def generate_mql5_wfo_v20(symbol):
    csv_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_v20_{symbol}.csv")
    if not os.path.exists(csv_path):
        print(f"Dataset for {symbol} not found.")
        return
        
    df = pd.read_csv(csv_path)
    df = df[df['Time'].str.len() >= 10]
    df['Time'] = pd.to_datetime(df['Time'], format='mixed', errors='coerce')
    df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
    
    start_date = df['Time'].min()
    end_date = df['Time'].max()
    current_train_start = start_date
    
    code = f"//+------------------------------------------------------------------+\n"
    code += f"//| XGBoost Model WFO V20 (Dynamic Event-Driven) - {symbol}\n"
    code += f"//+------------------------------------------------------------------+\n"
    code += f"// Features: {', '.join(FEATURES)}\n\n"
    
    routing_code = f"double XGBoost_Predict_WFO_v20_{symbol}(double &features[], int current_year, int current_month) {{\n"
    
    last_func_name = ""
    
    while True:
        current_train_end = current_train_start + pd.DateOffset(months=TRAIN_MONTHS)
        current_test_end = current_train_end + pd.DateOffset(months=TEST_MONTHS)
        
        if current_test_end > end_date + pd.DateOffset(months=1):
            break
            
        train_mask = (df['Time'] >= current_train_start) & (df['Time'] < current_train_end)
        test_mask = (df['Time'] >= current_train_end) & (df['Time'] < current_test_end)
        
        df_train = df[train_mask]
        df_test = df[test_mask]
        
        if len(df_train) < 50:
            current_train_start += pd.DateOffset(months=TEST_MONTHS)
            continue
            
        X_train = df_train[FEATURES].values
        y_train = df_train['Target_Label'].values
        # Sample weights: Abs ReturnPct forces model to care more about the TP size vs the SL size
        w_train = np.abs(df_train['Target_ReturnPct'].values)
        
        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train)
        
        # Simple static model for robustness (V20 Dynamic doesn't need Optuna overfitting)
        model = xgb.XGBClassifier(
            max_depth=4, 
            learning_rate=0.05, 
            n_estimators=100, 
            objective='binary:logistic',
            random_state=42
        )
        
        model.fit(X_train_sc, y_train, sample_weight=w_train)
        
        test_year = current_train_end.year
        test_month = current_train_end.month
        func_name = f"predict_V20_{symbol}_{test_year}_{test_month}"
        last_func_name = func_name
        
        booster = model.get_booster()
        trees = booster.get_dump()
        
        # Transpile Scaler
        code += f"double {func_name}(double &f[]) {{\n"
        code += f"    double scaled[{len(FEATURES)}];\n"
        for i in range(len(FEATURES)):
            code += f"    scaled[{i}] = (f[{i}] - ({scaler.center_[i]:.5f})) / ({scaler.scale_[i]:.5f});\n"
        
        # Transpile Trees
        code += f"    double sum = 0.0;\n"
        for tree_idx, tree_str in enumerate(trees):
            code += f"    // Tree {tree_idx}\n"
            lines = tree_str.strip().split('\n')
            for line in lines:
                if 'leaf' in line:
                    node, leaf_val = line.split(':leaf=')
                    code += f"    sum += {float(leaf_val):.6f};\n"
                else:
                    # Example: 0:[f0<1.23] yes=1,no=2,missing=1
                    pass # We need to properly parse trees. I will use a simplified tree parser.
                    
        # Simplified Tree Parser
        def parse_tree_recursive(lines_dict, node_id, indent="    "):
            line = lines_dict[node_id]
            if 'leaf' in line:
                val = line.split('leaf=')[1]
                return f"{indent}sum += {float(val)};\n"
            else:
                condition = line.split('[f')[1].split(']')[0]
                feat_idx = int(condition.split('<')[0])
                thresh = float(condition.split('<')[1])
                yes_node = line.split('yes=')[1].split(',')[0]
                no_node = line.split('no=')[1].split(',')[0]
                missing_node = line.split('missing=')[1]
                
                c = f"{indent}if(scaled[{feat_idx}] < {thresh}) {{\n"
                c += parse_tree_recursive(lines_dict, yes_node, indent + "    ")
                c += f"{indent}}} else {{\n"
                c += parse_tree_recursive(lines_dict, no_node, indent + "    ")
                c += f"{indent}}}\n"
                return c

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
        
        end_m = test_month + TEST_MONTHS
        if end_m <= 12:
            routing_code += f"    if(current_year == {test_year} && current_month >= {test_month} && current_month < {end_m}) return {func_name}(features);\n"
        else:
            routing_code += f"    if((current_year == {test_year} && current_month >= {test_month}) || (current_year == {test_year+1} && current_month < {end_m - 12})) return {func_name}(features);\n"
            
        print(f"[{symbol} - {test_year} M{test_month}] V20 Trained.")
        current_train_start += pd.DateOffset(months=TEST_MONTHS)
        
    if last_func_name != "":
        routing_code += f"    // Fallback para OOS puro / Live trading\n    return {last_func_name}(features);\n}}\n"
    else:
        routing_code += "    return 0.0;\n}\n"
        
    final_code = code + routing_code
    
    out_path = os.path.join(MODELS_DIR, f"XGBoost_Model_WFO_v20_{symbol}.mqh")
    with open(out_path, "w") as f:
        f.write(final_code)
    print(f"[{symbol}] Modulo V20 guardado en: {out_path}\n")

if __name__ == "__main__":
    print("--- V20 Dynamic WFO ---")
    for sym in SYMBOLS:
        generate_mql5_wfo_v20(sym)

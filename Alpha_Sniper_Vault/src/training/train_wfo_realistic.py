import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import os
import math
import json
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5'

FEATURES = [
    'SignalType','HMAAccelF','MTFATRRatio','DistSynthH4','CandleDominance',
    'TWAPZScore','ATRRatioH','RSI','DistAsianHigh','DistAsianLow','RSIExt',
    'VolSpreadRatio','Spread','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign',
    'Feature_VPivotMonotonic','RSI_Memory_State','OppositeBarsCount','Regime_ATR_D1',
    'Regime_ADX_H1','PriceDevATR','BuildupLength','DayOfWeek','DistRunwayHMA200','BarsVolShock'
]

def generate_tree_code(booster, features, scaler, func_name):
    df = booster.trees_to_dataframe()
    
    try:
        config = json.loads(booster.save_config())
        base_score_str = config['learner']['learner_model_param']['base_score'].strip('[]')
        base_score = float(base_score_str)
    except:
        base_score = 0.5
        
    center = scaler.center_.tolist()
    scale = scaler.scale_.tolist()
    
    code = f"double {func_name}(const double &features[]) {{\n"
    code += f"    double f[{len(features)}];\n"
    for i in range(len(features)):
        code += f"    f[{i}] = (features[{i}] - ({center[i]:.5f})) / ({scale[i]:.5f});\n"
        
    try:
        base_margin = -math.log(1.0 / base_score - 1.0) if base_score != 0.5 else 0.0
    except:
        base_margin = 0.0
        
    code += f"\n    double sum = {base_margin};\n\n"
    
    trees = df['Tree'].unique()
    for tree_id in trees:
        tree_df = df[df['Tree'] == tree_id].set_index('ID')
        
        def build_node(node_id, indent_level):
            row = tree_df.loc[node_id]
            indent = "    " * indent_level
            if row['Feature'] == 'Leaf':
                return f"{indent}sum += {row['Gain']};\n"
            
            feat_val = row['Feature']
            if str(feat_val).startswith('f') and str(feat_val)[1:].isdigit():
                feature_idx = int(str(feat_val).replace('f', ''))
            else:
                feature_idx = features.index(feat_val)

            split_val = row['Split']
            yes_node = row['Yes']
            no_node = row['No']
            
            node_code = f"{indent}if(f[{feature_idx}] < {split_val}) {{\n"
            node_code += build_node(yes_node, indent_level + 1)
            node_code += f"{indent}}} else {{\n"
            node_code += build_node(no_node, indent_level + 1)
            node_code += f"{indent}}}\n"
            return node_code

        root_id = f"{tree_id}-0"
        code += build_node(root_id, 1)
        
    code += "    return 1.0 / (1.0 + MathExp(-sum));\n"
    code += "}\n\n"
    return code

def run_wfo_for_symbol(sym):
    print(f"\n--- WFO para {sym} ---")
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_{sym}.csv')
    if not os.path.exists(fp): return
    
    df = pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    df['Time'] = pd.to_datetime(df['Time'])
    df['Year'] = df['Time'].dt.year
    
    years = range(2017, 2027)
    
    full_code = f"//+------------------------------------------------------------------+\n"
    full_code += f"//| XGBoost_Model_WFO_{sym}.mqh\n"
    full_code += f"//| Entrenamiento Walk-Forward (Ventana de 2 anios -> Opera 1 anio)\n"
    full_code += f"//+------------------------------------------------------------------+\n\n"
    
    # Store thresholds in a function
    thresholds = {}
    
    for test_year in years:
        train_years = [test_year - 2, test_year - 1]
        
        train_df = df[df['Year'].isin(train_years)]
        test_df = df[df['Year'] == test_year]
        
        if len(train_df) < 100:
            print(f"[{sym} - {test_year}] No hay suficientes datos para entrenar.")
            continue
            
        X_tr = train_df[FEATURES]
        y_tr = train_df['Label']
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_tr)
        
        # Hyperparameters chosen logically to prevent massive overfit
        params = {
            'max_depth': 4,
            'learning_rate': 0.02,
            'n_estimators': 80,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,
            'random_state': 42,
            'eval_metric': 'logloss',
            'n_jobs': 1
        }
        
        model = xgb.XGBClassifier(**params)
        model.fit(X_tr_sc, y_tr)
        
        prob_tr = model.predict_proba(X_tr_sc)[:,1]
        # Extraemos threshold SIN MIRAR AL FUTURO
        thr = np.percentile(prob_tr, 80)
        thresholds[test_year] = thr
        
        print(f"[{sym} - {test_year}] Modelo Entrenado. Threshold: {thr:.4f}")
        
        # Generar codigo C++ para el modelo del anio
        func_name = f"Predict_{sym}_{test_year}"
        tree_code = generate_tree_code(model.get_booster(), FEATURES, scaler, func_name)
        full_code += tree_code
        
    # Construir funcion maestra de ruteo
    full_code += f"double XGBoost_Predict_WFO_{sym}(const double &features[], int year, double &out_threshold) {{\n"
    full_code += f"    if(ArraySize(features) != {len(FEATURES)}) {{\n"
    full_code += f"        Print(\"Error: Feature count mismatch in {sym}. Expected {len(FEATURES)}\");\n"
    full_code += f"        return 0.0;\n"
    full_code += f"    }}\n\n"
    
    full_code += "    if(year < 2017) year = 2017;\n"
    full_code += "    if(year > 2026) year = 2026;\n\n"
    
    full_code += "    switch(year) {\n"
    for y, thr in thresholds.items():
        full_code += f"        case {y}:\n"
        full_code += f"            out_threshold = {thr:.5f};\n"
        full_code += f"            return Predict_{sym}_{y}(features);\n"
    full_code += "        default:\n"
    full_code += "            out_threshold = 0.5;\n"
    full_code += "            return 0.0;\n"
    full_code += "    }\n"
    full_code += "}\n"
    
    out_path = os.path.join(OUT_DIR, f'XGBoost_Model_WFO_{sym}.mqh')
    with open(out_path, 'w') as f:
        f.write(full_code)
    print(f"[{sym}] Exportado a {out_path}")

run_wfo_for_symbol('XAUUSD')
run_wfo_for_symbol('EURUSD')
run_wfo_for_symbol('USDJPY')
print("\n[OK] ENTRENAMIENTO WFO COMPLETADO.")
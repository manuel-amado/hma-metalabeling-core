import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import os
import math
import json
import glob
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Models'

# v17/v16.1 Features
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
            indent = "    " * indent_level
            row = tree_df.loc[node_id]
            if row['Feature'] == 'Leaf':
                return f"{indent}sum += {row['Gain']};\n"

            feat_val = row['Feature']
            if feat_val.startswith('f'): feature_idx = int(feat_val[1:])
            elif feat_val in features:
                feature_idx = features.index(feat_val)
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


def run_wfo_for_symbol(sym, start_year=2015, end_year=2026, train_window=2):
    print(f"\n--- WFO Estricto para {sym} ({start_year}-{end_year}) ---")
    
    # Cargar todos los datasets que existan para este simbolo (por si hay archivos segmentados por años)
    all_files = glob.glob(os.path.join(DATA_DIR, f'*v17*{sym}*.csv'))
    
    if not all_files:
        print(f"Error: No se encontraron datasets V17 para {sym}.")
        return
        
    df_list = []
    for fp in all_files:
        temp_df = pd.read_csv(fp)
        df_list.append(temp_df)
        
    df = pd.concat(df_list, ignore_index=True)
    df = df.dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    df['Time'] = pd.to_datetime(df['Time'], format='mixed')
    df['Year'] = df['Time'].dt.year
    df = df.sort_values('Time')
    
    min_year_avail = df['Year'].min()
    print(f"Datos disponibles desde: {min_year_avail} hasta {df['Year'].max()}")
    
    if min_year_avail > start_year - train_window:
        print(f"ADVERTENCIA: Para operar OOS en {start_year}, necesitas datos desde {start_year - train_window}.")
        print(f"Actualmente tus datos empiezan en {min_year_avail}.")
        print("El WFO ignorara los años que no tengan historial suficiente y comenzara cuando pueda.")
    
    years = range(start_year, end_year + 1)
    
    full_code = f"//+------------------------------------------------------------------+\n"
    full_code += f"//| XGBoost_Model_WFO_{sym}.mqh\n"
    full_code += f"//| Entrenamiento Walk-Forward Estricto ({train_window} anios IS -> 1 anio OOS)\n"
    full_code += f"//+------------------------------------------------------------------+\n\n"
    
    thresholds = {}
    valid_years = []
    
    for test_year in years:
        train_years = [test_year - i for i in range(train_window, 0, -1)]
        
        train_df = df[df['Year'].isin(train_years)]
        
        if len(train_df) < 500:
            print(f"[{sym} - {test_year}] SALTADO: No hay suficientes datos previos {train_years} (Filas: {len(train_df)}).")
            continue
            
        X_tr = train_df[FEATURES]
        y_tr = train_df['Label']
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_tr)
        
        # Hyperparameters conservadores para WFO (evitar overfitting en ventanas cortas)
        params = {
            'max_depth': 3,
            'learning_rate': 0.05,
            'n_estimators': 80,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'gamma': 0.5,
            'random_state': 42,
            'eval_metric': 'logloss',
            'n_jobs': -1
        }
        
        # En caso de imbalance
        scale_pos = len(y_tr[y_tr==0]) / len(y_tr[y_tr==1]) if sum(y_tr) > 0 else 1.0
        params['scale_pos_weight'] = scale_pos
        
        model = xgb.XGBClassifier(**params)
        model.fit(X_tr_sc, y_tr)
        
        prob_tr = model.predict_proba(X_tr_sc)[:,1]
        
        # Calibracion dinamica del threshold al percentil 75 del IS
        thr = np.percentile(prob_tr, 75)
        thresholds[test_year] = thr
        valid_years.append(test_year)
        
        print(f"[{sym} - {test_year}] Entrenado usando {train_years}. Ops: {len(train_df)} | Threshold IS: {thr:.4f}")
        
        func_name = f"Predict_WFO_{sym}_{test_year}"
        tree_code = generate_tree_code(model.get_booster(), FEATURES, scaler, func_name)
        full_code += tree_code
        
    if not valid_years:
        print(f"[{sym}] ERROR: Ningun modelo pudo ser entrenado.")
        return
        
    first_valid = min(valid_years)
    last_valid = max(valid_years)
    
    # Switch/Case Maestro
    full_code += f"double XGBoost_Predict_WFO_{sym}(const double &features[], int year, double &out_threshold) {{\n"
    
    # Manejo de fallback para años sin modelo
    full_code += f"    if(year < {first_valid}) year = {first_valid};\n"
    full_code += f"    if(year > {last_valid}) year = {last_valid};\n\n"
    
    full_code += "    switch(year) {\n"
    for y, thr in thresholds.items():
        full_code += f"        case {y}:\n"
        full_code += f"            out_threshold = {thr:.5f};\n"
        full_code += f"            return Predict_WFO_{sym}_{y}(features);\n"
    full_code += "        default:\n"
    full_code += f"            out_threshold = {thresholds[last_valid]:.5f};\n"
    full_code += f"            return Predict_WFO_{sym}_{last_valid}(features);\n"
    full_code += "    }\n"
    full_code += "}\n"
    
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f'XGBoost_Model_WFO_{sym}.mqh')
    with open(out_path, 'w') as f:
        f.write(full_code)
    print(f"[{sym}] Módulo WFO guardado exitosamente en: {out_path}\n")

if __name__ == "__main__":
    assets = ['XAUUSD', 'EURUSD', 'USDJPY', 'AUDUSD']
    for a in assets:
        run_wfo_for_symbol(a, start_year=2015, end_year=2026, train_window=2)

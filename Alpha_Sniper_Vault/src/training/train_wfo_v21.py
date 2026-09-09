import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler
import os
import math
import json
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5'

FEATURES_V11_3 = [
    'SignalType', 'HMAAccelF', 'MTFATRRatio', 'DistSynthH4', 'BarsVolShock',
    'TWAPZScore', 'ATRRatioH', 'RSI', 'DistAsianHigh', 'DistAsianLow', 'RSIExt',
    'VolSpreadRatio', 'Spread', 'TrigRejTail', 'RibbonSpreadStd', 'Feature_RibbonAlign',
    'Feature_VPivotMonotonic', 'RSI_Memory_State', 'OppositeBarsCount'
]

if not mt5.initialize():
    print("MT5 init failed")
    quit()

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    wma_half = wma(s, int(period / 2))
    wma_full = wma(s, period)
    diff = (2 * wma_half) - wma_full
    return wma(diff, int(np.sqrt(period)))

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
            if row['Feature'] == 'Leaf': return f"{indent}sum += {row['Gain']};\n"
            
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

        code += build_node(f"{tree_id}-0", 1)
        
    code += "    return 1.0 / (1.0 + MathExp(-sum));\n}\n\n"
    return code

def relabel_and_train_wfo(sym):
    print(f"\n--- WFO V21 para {sym} ---")
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_{sym}.csv')
    if not os.path.exists(fp): 
        print(f"Dataset not found: {fp}")
        return
    
    # 1. Fetch M15 Data
    print("Fetching MT5 Data...")
    rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 200000)
    if rates is None: return
    df_mt5 = pd.DataFrame(rates)
    df_mt5['time'] = pd.to_datetime(df_mt5['time'], unit='s')
    df_mt5.set_index('time', inplace=True)
    df_mt5['close'] = df_mt5['close'].astype(float)
    df_mt5['HMA_50'] = hma(df_mt5['close'], 50)
    df_mt5.dropna(inplace=True)
    
    times = df_mt5.index.values
    closes = df_mt5['close'].values
    hma50s = df_mt5['HMA_50'].values
    
    # 2. Load Features CSV
    df_feat = pd.read_csv(fp).dropna(subset=FEATURES_V11_3).reset_index(drop=True)
    df_feat['Time'] = pd.to_datetime(df_feat['Time'])
    
    new_labels = []
    
    print("Re-etiquetando dataset (Baseline HMA 50 Exit)...")
    for idx, row in df_feat.iterrows():
        t = row['Time'].to_datetime64()
        sig = row['SignalType']
        
        idx_mt5 = np.searchsorted(times, t)
        if idx_mt5 >= len(times) - 1 or times[idx_mt5] != t:
            new_labels.append(np.nan)
            continue
            
        entry_price = closes[idx_mt5]
        label = 0
        
        for i in range(idx_mt5 + 1, min(idx_mt5 + 200, len(times))):
            current_close = closes[i]
            current_hma = hma50s[i]
            
            exit_triggered = False
            if sig == 0 and current_close < current_hma: exit_triggered = True
            if sig == 1 and current_close > current_hma: exit_triggered = True
            
            if exit_triggered:
                profit = (current_close - entry_price) if sig == 0 else (entry_price - current_close)
                if sym == 'XAUUSD' and profit >= 0.50: label = 1
                elif sym == 'EURUSD' and profit >= 0.00050: label = 1
                elif sym == 'USDJPY' and profit >= 0.050: label = 1
                break
        
        new_labels.append(label)
        
    df_feat['NewLabel'] = new_labels
    df_feat.dropna(subset=['NewLabel'], inplace=True)
    print(f"Dataset Etiquetado. Win Rate de la nueva estrategia: {df_feat['NewLabel'].mean()*100:.1f}%")
    
    # 3. WFO Training
    df_feat['Year'] = df_feat['Time'].dt.year
    years = range(2017, 2027)
    
    full_code = f"//+------------------------------------------------------------------+\n"
    full_code += f"//| XGBoost_Model_WFO_v21_{sym}.mqh\n"
    full_code += f"//| Entrenamiento Walk-Forward para V21 (Re-etiquetado Baseline HMA)\n"
    full_code += f"//+------------------------------------------------------------------+\n\n"
    
    thresholds = {}
    
    for test_year in years:
        train_years = [test_year - 2, test_year - 1]
        train_df = df_feat[df_feat['Year'].isin(train_years)]
        if len(train_df) < 100: continue
            
        X_tr = train_df[FEATURES_V11_3]
        y_tr = train_df['NewLabel']
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_tr)
        
        params = {
            'max_depth': 4, 'learning_rate': 0.02, 'n_estimators': 80,
            'subsample': 0.8, 'colsample_bytree': 0.8, 'gamma': 0.1,
            'random_state': 42, 'eval_metric': 'logloss', 'n_jobs': 1
        }
        
        model = xgb.XGBClassifier(**params)
        model.fit(X_tr_sc, y_tr)
        
        prob_tr = model.predict_proba(X_tr_sc)[:,1]
        thr = np.percentile(prob_tr, 80)
        thresholds[test_year] = thr
        
        func_name = f"Predict_v21_{sym}_{test_year}"
        tree_code = generate_tree_code(model.get_booster(), FEATURES_V11_3, scaler, func_name)
        full_code += tree_code
        
    full_code += f"double XGBoost_Predict_WFO_v21_{sym}(const double &features[], int year, double &out_threshold) {{\n"
    full_code += f"    if(ArraySize(features) != {len(FEATURES_V11_3)}) return 0.0;\n"
    full_code += "    if(year < 2017) year = 2017;\n    if(year > 2026) year = 2026;\n    switch(year) {\n"
    for y, thr in thresholds.items():
        full_code += f"        case {y}: out_threshold = {thr:.5f}; return Predict_v21_{sym}_{y}(features);\n"
    full_code += "        default: out_threshold = 0.5; return 0.0;\n    }\n}\n"
    
    out_path = os.path.join(OUT_DIR, f'XGBoost_Model_WFO_v21_{sym}.mqh')
    with open(out_path, 'w') as f: f.write(full_code)
    print(f"[{sym}] Exportado a {out_path}")

relabel_and_train_wfo('XAUUSD')
relabel_and_train_wfo('EURUSD')
relabel_and_train_wfo('USDJPY')
mt5.shutdown()
print("\n[OK] ENTRENAMIENTO WFO V21 COMPLETADO.")
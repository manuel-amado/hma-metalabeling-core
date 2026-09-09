import os
import pandas as pd
import numpy as np
import xgboost as xgb
import optuna
from sklearn.preprocessing import RobustScaler
import warnings
warnings.filterwarnings('ignore')
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODELS_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Models"

FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4", "CandleDominance", "TWAPZScore", 
    "ATRRatioH", "RSI", "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio", "Spread",
    "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign", "VPivotMonotonic", "RSIMemory", 
    "OppositeBarsCount", "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", 
    "PandasDOW", "DistRunwayHMA200", "BarsVolShock", "Time_Sine", "Time_Cosine", "PainIndex"
]
TARGET_CLASS = "Label"

TRAIN_MONTHS = 24
TEST_MONTHS = 6
N_TRIALS_OPTUNA = 15

def build_node(node_id, indent_level, tree_df, features):
    indent = "    " * indent_level
    row = tree_df[tree_df['ID'] == node_id].iloc[0]
    if row['Feature'] == 'Leaf': return f"{indent}sum += {row['Gain']};\n"
    feat_val = row['Feature']
    if feat_val.startswith('f'): feature_idx = int(feat_val[1:])
    elif feat_val in features: feature_idx = features.index(feat_val)
    else: feature_idx = features.index(feat_val)
    split_val = row['Split']
    yes_node = row['Yes']
    no_node = row['No']
    node_code = f"{indent}if(f[{feature_idx}] < {split_val}) {{\n"
    node_code += build_node(yes_node, indent_level + 1, tree_df, features)
    node_code += f"{indent}}} else {{\n"
    node_code += build_node(no_node, indent_level + 1, tree_df, features)
    node_code += f"{indent}}}\n"
    return node_code

def generate_tree_code(booster, features, scaler, func_name):
    import json
    import math
    code = f"double {func_name}(double &raw_f[]) {{\n    double f[29];\n"
    for i, col in enumerate(features):
        mean = scaler.center_[i]
        scale = scaler.scale_[i]
        code += f"    f[{i}] = (raw_f[{i}] - ({mean})) / {scale};\n"
    code += "\n    double sum = 0.0;\n\n"
    tree_df = booster.trees_to_dataframe()
    for tree_id in tree_df['Tree'].unique():
        code += f"    // Tree {tree_id}\n"
        code += build_node(f"{tree_id}-0", 1, tree_df, features)
        code += "\n"
        
    bs_str = json.loads(booster.save_config())['learner']['learner_model_param']['base_score']
    bs_val = float(bs_str[0]) if isinstance(bs_str, list) else float(bs_str.strip('[]'))
    # convert probability to log odds margin
    margin = 0.0 if bs_val == 0.5 else -math.log(1.0 / bs_val - 1.0)
    code += f"    return 1.0 / (1.0 + MathExp(-(sum + ({margin}))));\n}}\n"
    return code

def optimize_hyperparams(X_train, y_train, w_train):
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 2, 5),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 30, 80),
            'subsample': trial.suggest_float('subsample', 0.5, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
            'objective': 'binary:logistic',
            'random_state': 42
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, sample_weight=w_train)
        preds = model.predict(X_train)
        return (preds == y_train).mean()
    
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS_OPTUNA, )
    return study.best_params

def run_agile_wfo(symbol):
    print(f"\n--- V19 Agile WFO para {symbol} ---")
    csv_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_v17_{symbol}.csv")
    if not os.path.exists(csv_path):
        print(f"[{symbol}] OMITIDO: Dataset no encontrado.")
        return
    df = pd.read_csv(csv_path)
    df = df[df['Time'].str.len() > 10]
    df['Time'] = pd.to_datetime(df['Time'], format='mixed', errors='coerce')
    df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
        
    mqh_filename = f"XGBoost_Model_WFO_v19_{symbol}.mqh"
    mqh_path = os.path.join(MODELS_DIR, mqh_filename)
    cpp_functions = []
    
    routing_code = f"double XGBoost_Predict_WFO_v19_{symbol}(double &features[], int current_year, int current_month, double threshold) {{\n"
    
    start_date = df['Time'].min()
    end_date = df['Time'].max()
    current_train_start = start_date
    while True:
        current_train_end = current_train_start + pd.DateOffset(months=TRAIN_MONTHS)
        current_test_end = current_train_end + pd.DateOffset(months=TEST_MONTHS)
        if current_test_end > end_date + pd.DateOffset(months=1): break
        train_mask = (df['Time'] >= current_train_start) & (df['Time'] < current_train_end)
        df_train = df[train_mask]
        if len(df_train) < 100:
            current_train_start += pd.DateOffset(months=TEST_MONTHS)
            continue
        X_train = df_train[FEATURES].values
        y_train = df_train[TARGET_CLASS].values
        w_train = np.abs(df_train['ReturnPct'].values)
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        best_params = optimize_hyperparams(X_tr_sc, y_train, w_train)
        best_params['objective'] = 'binary:logistic'
        best_params['random_state'] = 42
        model = xgb.XGBClassifier(**best_params)
        model.fit(X_tr_sc, y_train, sample_weight=w_train)
        test_year = current_train_end.year
        test_month = current_train_end.month
        func_name = f"predict_{symbol}_{test_year}_{test_month}"
        cpp_functions.append(generate_tree_code(model.get_booster(), FEATURES, scaler, func_name))
        
        end_m = test_month + TEST_MONTHS
        if end_m <= 12:
            routing_code += f"    if(current_year == {test_year} && current_month >= {test_month} && current_month < {end_m}) return {func_name}(features);\n"
        else:
            routing_code += f"    if((current_year == {test_year} && current_month >= {test_month}) || (current_year == {test_year+1} && current_month < {end_m - 12})) return {func_name}(features);\n"
            
        print(f"[{symbol} - {test_year} M{test_month}] Entrenado. Accuracy Optuna: Depth={best_params['max_depth']} LR={best_params['learning_rate']:.3f}")
        current_train_start += pd.DateOffset(months=TEST_MONTHS)
    routing_code += f"    // Fallback para OOS puro / Live trading\n    return {func_name}(features);\n}}\n"
    with open(mqh_path, "w") as f:
        f.write("// --- V19 WFO (24M Train -> 6M Test | Binary Classification) ---\n\n")
        for func in cpp_functions: f.write(func + "\n")
        f.write(routing_code)
    print(f"[{symbol}] Modulo V19 guardado en: {mqh_path}")

if __name__ == "__main__":
    for sym in ["XAUUSD", "EURUSD", "USDJPY", "AUDUSD"]:
        run_agile_wfo(sym)

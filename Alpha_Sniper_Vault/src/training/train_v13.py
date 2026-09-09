import os
import pandas as pd
import numpy as np
import optuna
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import KFold
from sklearn.preprocessing import RobustScaler
import argparse
import warnings
import glob

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v13_universal.pkl")
args = parser.parse_args()

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODEL_PATH = args.model

FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
    "CandleDominance", "TWAPZScore", "ATRRatioH", "RSI",
    "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
    "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
    "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount"
]

def get_interleaved_masks(total_rows, n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=20):
    block_size = total_rows // n_blocks
    train_mask = np.zeros(total_rows, dtype=bool)
    test_mask = np.zeros(total_rows, dtype=bool)
    
    for i in range(n_blocks):
        start = i * block_size
        end = (i + 1) * block_size if i < n_blocks - 1 else total_rows
        if i in oos_blocks:
            test_mask[start:end] = True
        else:
            train_mask[start:end] = True

    # Purga (Embargo Institucional) de 20 barras M15
    for i in range(1, n_blocks):
        boundary = i * block_size
        prev_is_oos = (i - 1) in oos_blocks
        curr_is_oos = i in oos_blocks
        
        if prev_is_oos != curr_is_oos:
            purge_start = max(0, boundary - embargo_bars)
            purge_end = min(total_rows, boundary + embargo_bars)
            train_mask[purge_start:purge_end] = False
            test_mask[purge_start:purge_end] = False
            
    return train_mask, test_mask

def load_and_partition_data():
    all_files = glob.glob(os.path.join(DATA_DIR, "Alpha_Sweep_Dataset_v13_*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No V13 CSV files found in {DATA_DIR}")
        
    df_list = []
    train_masks_list = []
    test_masks_list = []
    
    for f in all_files:
        # Extract symbol from filename
        symbol = os.path.basename(f).replace('Alpha_Sweep_Dataset_v13_', '').replace('.csv', '')
        df_tmp = pd.read_csv(f)
        df_tmp['Symbol'] = symbol
        
        if 'SpreadATRRatio' in df_tmp.columns and 'Spread' not in df_tmp.columns:
            df_tmp.rename(columns={'SpreadATRRatio': 'Spread'}, inplace=True)
            
        if 'Label' not in df_tmp.columns:
            raise ValueError(f"Critical Error: 'Label' column not found in dataset {f}.")
            
        rows = len(df_tmp)
        # Apply interleaved masking per asset
        tr_mask, te_mask = get_interleaved_masks(rows, n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=20)
        
        df_list.append(df_tmp)
        train_masks_list.append(tr_mask)
        test_masks_list.append(te_mask)

    df = pd.concat(df_list, ignore_index=True)
    train_mask_global = np.concatenate(train_masks_list)
    test_mask_global = np.concatenate(test_masks_list)
    
    X = df[FEATURES]
    y = df['Label']
    
    return X, y, df, train_mask_global, test_mask_global

def objective(trial, X, y, df):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 200),
        'max_depth': trial.suggest_int('max_depth', 3, 5),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 0.7),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.7),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
        'gamma': trial.suggest_float('gamma', 1e-3, 5.0, log=True),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True)
    }

    # KFold for Optuna since data is chronologically disjointed blocks
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    precisions = []

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        df_test = df.iloc[test_index]
        
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        scale_pos = len(y_train[y_train==0]) / len(y_train[y_train==1]) if sum(y_train) > 0 else 1.0
        
        model = XGBClassifier(
            **params,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric='logloss',
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        proba = model.predict_proba(X_test_scaled)[:, 1]
        
        threshold = np.percentile(proba, 75)
        y_pred = (proba >= threshold).astype(int)
        
        wins = df_test[(y_pred == 1) & (df_test['Label'] == 1)]
        trades = sum(y_pred)
        wr = len(wins) / trades if trades > 0 else 0.0
        precisions.append(wr)
            
    mean_prec = np.mean(precisions)
    std_prec = np.std(precisions)
    
    score = mean_prec - (2.0 * std_prec)
    return score

def main():
    print("[1/5] Cargando dataset y particionando bloques intercalados por activo...")
    X, y, df, train_mask, test_mask = load_and_partition_data()
    print(f"Total Operaciones en log: {len(X)}")

    X_is = X[train_mask]
    y_is = y[train_mask]
    df_is = df[train_mask]
    
    print(f"Total Operaciones retenidas para IS (Train Global): {len(X_is)}")
    print(f"Total Operaciones para OOS (Ciegas): {sum(test_mask)}")
    print(f"Operaciones Purgadas en Fronteras: {len(X) - len(X_is) - sum(test_mask)}")

    print("[2/5] Optimizando hiperparametros con Penalizacion Temporal (Exclusivo en IS)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, X_is, y_is, df_is), n_trials=50)

    best_params = study.best_params
    print(f"Mejor Score IS (mu - 2*sigma): {study.best_value:.4f}")
    print("Mejores hiperparametros encontrados:", best_params)

    print("[3/5] Entrenando Modelo Universal (Zonas IS Globales)...")
    scaler = RobustScaler()
    X_is_scaled = scaler.fit_transform(X_is)
    scale_pos = len(y_is[y_is==0]) / len(y_is[y_is==1]) if sum(y_is) > 0 else 1.0
    
    final_model = XGBClassifier(
        **best_params,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )
    final_model.fit(X_is_scaled, y_is)

    # Calibrate Threshold strictly on IS
    proba_train = final_model.predict_proba(X_is_scaled)[:, 1]
    threshold = np.percentile(proba_train, 75)
    print(f"Umbral de Decisión Calibrado (Percentil 75 en IS): {threshold:.4f}")

    print("\n=======================================================")
    print("   REPORTE DE ZONAS OOS ABSOLUTAS (POR ACTIVO)         ")
    print("=======================================================")
    
    X_oos = X[test_mask]
    df_oos = df[test_mask].copy()
    
    if len(X_oos) == 0:
        print("ERROR: No hay datos OOS para evaluar.")
    else:
        X_oos_scaled = scaler.transform(X_oos)
        proba_oos = final_model.predict_proba(X_oos_scaled)[:, 1]
        df_oos['Pred'] = (proba_oos >= threshold).astype(int)
        
        symbols = df_oos['Symbol'].unique()
        for sym in symbols:
            df_sym = df_oos[df_oos['Symbol'] == sym]
            trades_df = df_sym[df_sym['Pred'] == 1]
            wins = trades_df[trades_df['Label'] == 1]
            losses = trades_df[trades_df['Label'] == 0]
            
            trades = len(trades_df)
            wr = len(wins) / trades * 100.0 if trades > 0 else 0.0
            
            gross_profit = sum([abs(x) for x in wins['ReturnPct']])
            gross_loss = sum([abs(x) if abs(x) > 0.05 else 0.05 for x in losses['ReturnPct']])
            pf = gross_profit / gross_loss if gross_loss > 0 else 999.0
            net = gross_profit - gross_loss
            
            print(f"[{sym}] Trades OOS: {trades} | Win Rate: {wr:.2f}% | PF: {pf:.3f} | Net Return: +{net:.2f}%")
            
    print("=======================================================\n")

    print("[4/5] Guardando binario del Modelo Universal...")
    artifact = {
        'model': final_model,
        'scaler': scaler,
        'features_activas': FEATURES,
        'threshold': threshold
    }
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f"Modelo Invariante guardado en {MODEL_PATH}")
    print("[5/5] Completado. Procede a exportar los MQH.")

if __name__ == "__main__":
    main()

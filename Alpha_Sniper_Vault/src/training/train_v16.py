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
parser.add_argument('--model', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v16_universal.pkl")
args = parser.parse_args()

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODEL_PATH = args.model

FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
    "CandleDominance", "TWAPZScore", "ATRRatioH", "RSI",
    "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
    "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
    "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount",
    "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", "DayOfWeek", "DistRunwayHMA200"
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
    all_files = glob.glob(os.path.join(DATA_DIR, "Alpha_Sweep_Dataset_v16_*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No v16 CSV files found in {DATA_DIR}")
        
    df_list = []
    train_masks_list = []
    test_masks_list = []
    pre_masks_list = []
    post_masks_list = []
    
    for f in all_files:
        # Extract symbol from filename
        symbol = os.path.basename(f).replace('Alpha_Sweep_Dataset_v16_', '').replace('.csv', '')
        df_tmp = pd.read_csv(f)
        df_tmp['Symbol'] = symbol
        
        if 'SpreadATRRatio' in df_tmp.columns and 'Spread' not in df_tmp.columns:
            df_tmp.rename(columns={'SpreadATRRatio': 'Spread'}, inplace=True)
            
        if 'Label' not in df_tmp.columns:
            raise ValueError(f"Critical Error: 'Label' column not found in dataset {f}.")
            
        rows = len(df_tmp)
        # Apply interleaved masking per asset
        tr_mask, te_mask = get_interleaved_masks(rows, n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=20)
        
        split_idx = int(rows * 0.55)
        pre_mask = np.zeros(rows, dtype=bool)
        pre_mask[:split_idx] = True
        post_mask = np.zeros(rows, dtype=bool)
        post_mask[split_idx:] = True
        
        df_list.append(df_tmp)
        train_masks_list.append(tr_mask)
        test_masks_list.append(te_mask)
        pre_masks_list.append(pre_mask)
        post_masks_list.append(post_mask)

    df = pd.concat(df_list, ignore_index=True)
    train_mask_global = np.concatenate(train_masks_list)
    test_mask_global = np.concatenate(test_masks_list)
    pre_mask_global = np.concatenate(pre_masks_list)
    post_mask_global = np.concatenate(post_masks_list)
    
    X = df[FEATURES]
    y = df['Label']
    
    return X, y, df, train_mask_global, test_mask_global, pre_mask_global, post_mask_global

def objective(trial, X, y, df, pre_mask, post_mask):
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

    # V14 BIMODAL EVALUATION: Pre-2021 vs Post-2021 using boolean masks
    X_pre = X[pre_mask]
    y_pre = y[pre_mask]
    df_pre = df[pre_mask]
    
    X_post = X[post_mask]
    y_post = y[post_mask]
    df_post = df[post_mask]

    # Train/Test Time Series Split per Era
    train_idx_pre = int(len(X_pre) * 0.7)
    train_idx_post = int(len(X_post) * 0.7)
    
    X_train = pd.concat([X_pre.iloc[:train_idx_pre], X_post.iloc[:train_idx_post]])
    y_train = pd.concat([y_pre.iloc[:train_idx_pre], y_post.iloc[:train_idx_post]])
    
    X_test_pre = X_pre.iloc[train_idx_pre:]
    y_test_pre = y_pre.iloc[train_idx_pre:]
    df_test_pre = df_pre.iloc[train_idx_pre:]
    
    X_test_post = X_post.iloc[train_idx_post:]
    y_test_post = y_post.iloc[train_idx_post:]
    df_test_post = df_post.iloc[train_idx_post:]

    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    scale_pos = len(y_train[y_train==0]) / len(y_train[y_train==1]) if sum(y_train) > 0 else 1.0
    
    model = XGBClassifier(
        **params,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric='logloss',
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluar en Ciclo Antiguo (Pre-2021)
    X_test_pre_scaled = scaler.transform(X_test_pre)
    proba_pre = model.predict_proba(X_test_pre_scaled)[:, 1]
    thresh_pre = np.percentile(proba_pre, 75)
    y_pred_pre = (proba_pre >= thresh_pre).astype(int)
    trades_pre = sum(y_pred_pre)
    wr_pre = len(df_test_pre[(y_pred_pre == 1) & (df_test_pre['Label'] == 1)]) / trades_pre if trades_pre > 0 else 0.0
    
    # Evaluar en Ciclo Nuevo (Post-2021)
    X_test_post_scaled = scaler.transform(X_test_post)
    proba_post = model.predict_proba(X_test_post_scaled)[:, 1]
    thresh_post = np.percentile(proba_post, 75)
    y_pred_post = (proba_post >= thresh_post).astype(int)
    trades_post = sum(y_pred_post)
    wr_post = len(df_test_post[(y_pred_post == 1) & (df_test_post['Label'] == 1)]) / trades_post if trades_post > 0 else 0.0
    
    # Fitness Function: Maximize minimum WinRate, penalize deviation between eras
    score = min(wr_pre, wr_post) - abs(wr_pre - wr_post)
    return score

def main():
    print("[1/5] Cargando dataset y particionando bloques intercalados por activo...")
    X, y, df, train_mask, test_mask, pre_mask, post_mask = load_and_partition_data()
    print(f"Total Operaciones en log: {len(X)}")

    X_is = X[train_mask]
    y_is = y[train_mask]
    df_is = df[train_mask]
    
    # Sub-masks for In-Sample only
    pre_mask_is = pre_mask[train_mask]
    post_mask_is = post_mask[train_mask]
    
    print(f"Total Operaciones retenidas para IS (Train Global): {len(X_is)}")
    print(f"Total Operaciones para OOS (Ciegas): {sum(test_mask)}")
    print(f"Operaciones Purgadas en Fronteras: {len(X) - len(X_is) - sum(test_mask)}")

    print("[2/5] Optimizando hiperparametros con Penalizacion Temporal (Exclusivo en IS)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, X_is, y_is, df_is, pre_mask_is, post_mask_is), n_trials=50)

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
            gross_loss = sum([abs(x) if abs(x) > 0.001 else 0.001 for x in losses['ReturnPct']])
            pf = gross_profit / gross_loss if gross_loss > 0 else 999.0
            
            # Riesgo Realista (1% por operacion)
            # Como el lote en Meta-Labeling fue fijo, el Profit Factor se mantiene.
            # Retorno Lineal Neto asumiendo -1% fijo por cada perdida.
            real_net = len(losses) * (pf - 1.0) * 1.0 # 1.0 es 1% de riesgo
            
            print(f"[{sym}] Trades OOS: {trades} | Win Rate: {wr:.2f}% | PF: {pf:.3f} | Real Net Return (1% Risk): {real_net:+.2f}%")
            
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


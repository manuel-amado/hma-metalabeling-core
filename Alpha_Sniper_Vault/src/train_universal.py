import os
import pandas as pd
import numpy as np
import optuna
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
import argparse
import warnings

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sweep_Dataset_XAUUSD.csv")
parser.add_argument('--model', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_m15_universal.pkl")
args = parser.parse_args()

DATA_PATH = args.data
MODEL_PATH = args.model

FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
    "BarsVolShock", "TWAPZScore", "ATRRatioH", "RSI",
    "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
    "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
    "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount"
]

def load_data():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df["Label"]
    return X, y, df

def get_interleaved_masks(total_rows, n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=200):
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

    # Purga (Embargo Institucional)
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

def objective(trial, X, y, df):
    # Restricciones Draconianas
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

    tscv = TimeSeriesSplit(n_splits=5)
    precisions = []

    for train_index, test_index in tscv.split(X):
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
        
        # Test on the top 10% most confident trades in the OOS fold
        threshold = np.percentile(proba, 90)
        y_pred = (proba >= threshold).astype(int)
        
        wins = df_test[(y_pred == 1) & (df_test['ReturnPct'] > 0)]
        trades = sum(y_pred)
        if trades == 0:
            precisions.append(0.0)
        else:
            wr = len(wins) / trades
            precisions.append(wr)
            
    mean_prec = np.mean(precisions)
    std_prec = np.std(precisions)
    
    # Penalizacion Sharpe (mu - 2*sigma)
    score = mean_prec - (2.0 * std_prec)
    return score

def main():
    print("[1/5] Cargando dataset completo (2015-2026)...")
    X, y, df = load_data()
    print(f"Total Operaciones en log: {len(X)}")

    print("[2/5] Aplicando Purga y Embargo Institucional...")
    # 15 trades equivalen a aprox. 2.5 a 3 dias operativos de margen, cumpliendo las >200 velas M15 de purga
    train_mask, test_mask = get_interleaved_masks(len(X), n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=15)
    
    X_is = X[train_mask]
    y_is = y[train_mask]
    df_is = df[train_mask]
    
    print(f"Total Operaciones retenidas para IS (Train): {len(X_is)}")
    print(f"Total Operaciones para OOS (Ciegas): {sum(test_mask)}")
    print(f"Operaciones Purgadas en Fronteras: {len(X) - len(X_is) - sum(test_mask)}")

    print("[3/5] Optimizando hiperparametros con Penalizacion Temporal (Exclusivo en IS)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, X_is, y_is, df_is), n_trials=50)

    best_params = study.best_params
    print(f"Mejor Score IS (mu - 2*sigma): {study.best_value:.4f}")
    print("Mejores hiperparametros encontrados:", best_params)

    print("[4/5] Entrenando Modelo Final (Zonas IS Purificadas)...")
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

    print("\n=======================================================")
    print("   REPORTE DE ZONAS OOS ABSOLUTAS (BLOQUES CIEGOS)     ")
    print("=======================================================")
    X_oos = X[test_mask]
    y_oos = y[test_mask]
    df_oos = df[test_mask]
    
    # El threshold se extrae desde IS para evitar data snooping
    proba_train = final_model.predict_proba(X_is_scaled)[:, 1]
    threshold = np.percentile(proba_train, 90)

    if len(X_oos) == 0:
        print("ERROR: No hay datos OOS para evaluar.")
    else:
        X_oos_scaled = scaler.transform(X_oos)
        proba_oos = final_model.predict_proba(X_oos_scaled)[:, 1]
        
        y_pred_oos = (proba_oos >= threshold).astype(int)
        
        wins = df_oos[(y_pred_oos == 1) & (df_oos['ReturnPct'] > 0)]
        losses = df_oos[(y_pred_oos == 1) & (df_oos['ReturnPct'] <= 0)]
        
        trades = sum(y_pred_oos)
        wr = len(wins) / trades * 100.0 if trades > 0 else 0.0
        
        gross_profit = sum(wins['ReturnPct'])
        gross_loss = abs(sum(losses['ReturnPct']))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999.0
        
        print(f"Operaciones Ejecutadas (OOS): {trades}")
        print(f"Win Rate OOS:                 {wr:.2f}%")
        print(f"Profit Factor OOS:            {profit_factor:.3f}")
        if profit_factor > 1.05:
            print("-> ESTADO: APROBADO. El edge se mantiene robusto en terreno ciego.")
        else:
            print("-> ESTADO: FALLO CRITICO (OVERFIT). El modelo colapsa en zonas no vistas.")
    print("=======================================================\n")

    print("[5/5] Guardando binario...")
    artifact = {
        'model': final_model,
        'scaler': scaler,
        'features_activas': FEATURES,
        'threshold': threshold
    }
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f"Modelo Invariante (OOS Purificado) guardado en {MODEL_PATH}")

if __name__ == "__main__":
    main()

import os
import pandas as pd
import numpy as np
import optuna
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_score
import warnings

warnings.filterwarnings("ignore")

# Configuration
DATA_PATH = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sweep_Dataset_XAUUSD.csv"
MODEL_PATH = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_m15_purgado.pkl"

# Top 15 Features derived from Information Gain in M15 Sweep
FEATURES = [
    "SignalType",
    "HMAAccelF",
    "MTFATRRatio",
    "DistSynthH4",
    "BarsVolShock",
    "TWAPZScore",
    "ATRRatioH",
    "RSI",
    "DistAsianHigh",
    "DistAsianLow",
    "RSIExt",
    "VolSpreadRatio",
    "Spread",
    "TrigRejTail",
    "RibbonSpreadStd",
    "Feature_RibbonAlign",
    "Feature_VPivotMonotonic",
    "RSI_Memory_State",
    "OppositeBarsCount"
]

def load_data():
    df = pd.read_csv(DATA_PATH, header=None, skiprows=1)
    df.columns = ["SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4", "BarsVolShock", "TWAPZScore", "ATRRatioH", "RSI", "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio", "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign", "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount", "GHOST", "ReturnPct", "Label"]
    df = df.drop(columns=["GHOST"])
    df.columns = df.columns.str.strip()
    df.dropna(inplace=True)
    return df

def objective(trial, X, y):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 2, 5),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 0.9),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9),
        'min_child_weight': trial.suggest_int('min_child_weight', 3, 10),
        'gamma': trial.suggest_float('gamma', 0.0, 0.5),
        'random_state': 42,
        'n_jobs': -1
    }
    
    tscv = TimeSeriesSplit(n_splits=5)
    precisions = []
    
    for train_index, val_index in tscv.split(X):
        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
        y_train, y_val = y.iloc[train_index], y.iloc[val_index]
        
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        model = XGBClassifier(**params)
        model.fit(X_train_scaled, y_train, eval_set=[(X_val_scaled, y_val)], verbose=False)
        
        preds = model.predict(X_val_scaled)
        if sum(preds) > 0:
            precisions.append(precision_score(y_val, preds))
        else:
            precisions.append(0.0)
            
    return np.mean(precisions)

def main():
    print("[1] Loading Data...")
    df = load_data()
    
    X = df[FEATURES]
    y = df['Label']
    
    print(f"Dataset Size: {len(df)}")
    print(f"Features: {len(FEATURES)}")
    
    print("\n[2] Running Optuna Optimization (100 trials)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X, y), n_trials=100)
    
    print("\nBest Parameters:", study.best_params)
    print("Best CV Precision:", study.best_value)
    
    print("\n[3] Training Final Model on Entire Dataset...")
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    best_model = XGBClassifier(**study.best_params, random_state=42)
    best_model.fit(X_scaled, y)
    
    print("\n[4] Saving Artifacts...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    artifact = {
        'model': best_model,
        'scaler': scaler,
        'features_activas': FEATURES,
        'threshold': 0.5
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    main()




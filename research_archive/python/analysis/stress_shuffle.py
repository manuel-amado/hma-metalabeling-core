import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import precision_score
import optuna
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data\Alpha_Sweep_Dataset_XAUUSD.csv'

def objective(trial, X, y):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 30, 100),
        'max_depth': trial.suggest_int('max_depth', 3, 7),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
        'subsample': trial.suggest_float('subsample', 0.5, 0.9),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0.0, 0.5)
    }
    
    tscv = TimeSeriesSplit(n_splits=5)
    scores = []
    
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        
        if sum(preds) > 0:
            score = precision_score(y_test, preds, zero_division=0)
            scores.append(score)
        else:
            scores.append(0.0)
            
    return np.mean(scores) if scores else 0.0

if __name__ == '__main__':
    print('🚨 MONTE CARLO LABEL SHUFFLING (STRESS TEST) 🚨')
    
    try:
        # Load exactly as train_m15 does to avoid Pandas parsing errors
        with open(DATA_PATH, 'r') as f:
            lines = f.readlines()
        
        header = lines[0].strip().split(',')
        data = []
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 21:
                # the 19th index is the 0.0 garbage. Let's just grab the known columns
                row = [float(p) for p in parts[:19]]
                # 20th is return_pct, 21st is label
                row.append(float(parts[-1])) # label
                data.append(row)
                
        df = pd.DataFrame(data)
        X = df.iloc[:, :19]
        y = df.iloc[:, 19].astype(int) # label is now at index 19
        
        print(f'Dataset cargado. Total de muestras: {len(X)}')
        
        np.random.seed(42)
        y_shuffled = np.random.permutation(y)
        y_shuffled_series = pd.Series(y_shuffled)
        
        print('Etiquetas mezcladas aleatoriamente. Iniciando búsqueda bayesiana de ruido...')
        
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: objective(trial, X, y_shuffled_series), n_trials=30)
        
        best_score = study.best_value
        print(f'\n=========================================')
        print(f'🎯 Precisión Out-of-Sample (Shuffle): {best_score:.4f}')
        print(f'=========================================')
        
        if best_score > 0.55:
            print('❌ ALERTA CRÍTICA: El modelo encontró patrones en datos aleatorios. Hay Data Leakage.')
        else:
            print('✅ PRUEBA SUPERADA: El modelo colapsó al azar puro (~50%). La ventaja original es real.')
            
    except Exception as e:
        print(f'Error: {e}')

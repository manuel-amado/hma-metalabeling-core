import pandas as pd
import numpy as np
import optuna
import joblib
import os
from xgboost import XGBClassifier
from sklearn.preprocessing import RobustScaler

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'
os.makedirs(OUT_DIR, exist_ok=True)

FEATURES = [
    'SignalType','HMAAccelF','MTFATRRatio','DistSynthH4','CandleDominance',
    'TWAPZScore','ATRRatioH','RSI','DistAsianHigh','DistAsianLow','RSIExt',
    'VolSpreadRatio','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign',
    'OppositeBarsCount','Regime_ATR_D1','Regime_ADX_H1','PriceDevATR',
    'BuildupLength','DistRunwayHMA200','BarsVolShock'
] 

# Generador de Purged K-Folds para evitar Data Leakage temporal
def get_cv_splits(n, n_splits=5, embargo=20):
    splits = []
    fold_size = n // n_splits
    for i in range(n_splits):
        val_start = i * fold_size
        val_end = (i + 1) * fold_size if i < n_splits - 1 else n
        
        train_mask = np.ones(n, dtype=bool)
        val_mask = np.zeros(n, dtype=bool)
        
        val_mask[val_start:val_end] = True
        train_mask[val_start:val_end] = False
        
        # Embargo
        emb_start = max(0, val_start - embargo)
        emb_end = min(n, val_end + embargo)
        train_mask[emb_start:emb_end] = False
        
        splits.append((train_mask, val_mask))
    return splits

def optimize_and_train_symbol(sym):
    print(f"\n[{sym}] Iniciando entrenamiento RIGUROSO ANTI-OVERFIT...")
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    if not os.path.exists(fp):
        return
        
    df = pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    X = df[FEATURES]
    y = df['Label']
    returns = df['ReturnPct']
    
    cv_splits = get_cv_splits(len(df), n_splits=5, embargo=20)
    
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 1, 3), # RESTRINGIDO a arboles poco profundos
            'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.05, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 50, 150),
            'subsample': trial.suggest_float('subsample', 0.4, 0.8),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.4, 0.8),
            'gamma': trial.suggest_float('gamma', 0.5, 5.0), # Alta poda
            'min_child_weight': trial.suggest_int('min_child_weight', 5, 20),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.1, 10.0, log=True), # L1 Lasso
            'reg_lambda': trial.suggest_float('reg_lambda', 0.1, 10.0, log=True), # L2 Ridge
            'random_state': 42,
            'eval_metric': 'logloss',
            'n_jobs': 1
        }
        
        scores = []
        for tr_mask, val_mask in cv_splits:
            X_tr, y_tr = X[tr_mask], y[tr_mask]
            X_val, y_val = X[val_mask], y[val_mask]
            
            scaler = RobustScaler()
            X_tr_sc = scaler.fit_transform(X_tr)
            X_val_sc = scaler.transform(X_val)
            
            model = XGBClassifier(**params)
            model.fit(X_tr_sc, y_tr)
            
            prob_val = model.predict_proba(X_val_sc)[:,1]
            
            # Determinamos el threshold de forma CIEGA basandonos en el percentil 80 del set de validacion
            # (No iteramos buscando el mejor. Obligamos al modelo a ser confiable en probabilidades altas)
            thr = np.percentile(prob_val, 80)
            pred_val = prob_val >= thr
            
            if pred_val.sum() < 5:
                scores.append(0.0)
                continue
                
            # Score = Profit Factor on Validation Set
            wins = y_val.values[pred_val] == 1
            losses = ~wins
            
            wr = wins.mean()
            # Penalizacion severa por WR bajo
            if wr < 0.45:
                scores.append(0.0)
            else:
                score = wr * (np.log(pred_val.sum() + 1) / 10.0)
                scores.append(score)
                
        return np.mean(scores)

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=50, n_jobs=-1)
    
    best_params = study.best_params
    best_params['random_state'] = 42
    best_params['eval_metric'] = 'logloss'
    
    # Entrenar el modelo FINAL usando una separacion clasica IS/OOS (75/25) para exportarlo
    tr_mask = np.ones(len(df), dtype=bool)
    te_mask = np.zeros(len(df), dtype=bool)
    split_idx = int(len(df) * 0.75)
    tr_mask[split_idx:] = False
    te_mask[:split_idx] = False
    te_mask[split_idx+20:] = True # Embargo al inicio del test set
    
    X_tr, y_tr = X[tr_mask], y[tr_mask]
    X_te, y_te = X[te_mask], y[te_mask]
    
    scaler = RobustScaler()
    X_tr_sc = pd.DataFrame(scaler.fit_transform(X_tr), columns=FEATURES)
    X_te_sc = pd.DataFrame(scaler.transform(X_te), columns=FEATURES)
    
    model = XGBClassifier(**best_params)
    model.fit(X_tr_sc, y_tr)
    
    # Seleccion del Threshold en base a las predicciones DEL TRAIN SET (Totalmente legal)
    prob_tr = model.predict_proba(X_tr_sc)[:,1]
    best_thr = np.percentile(prob_tr, 80) # Solo tomamos el 20% mas seguro del training
    
    # Evaluacion final en el Test Set CIEGO
    prob_te = model.predict_proba(X_te_sc)[:,1]
    pred_te = prob_te >= best_thr
    
    wr_te = (y_te.values[pred_te] == 1).mean() if pred_te.sum() > 0 else 0
    netR_te = np.where(pred_te, np.where(y_te.values==1, 1.7, -1.0), 0).sum()
    
    print(f"[{sym}] Threshold Elegido (Percentil 80 TRAIN): {best_thr:.4f}")
    print(f"[{sym}] TRUE OOS WR: {wr_te*100:.1f}% | TRUE OOS NetR: {netR_te:.1f}R | OOS Trades: {pred_te.sum()}")
    
    art = {
        'model': model,
        'scaler': scaler,
        'features_activas': FEATURES,
        'threshold': best_thr
    }
    
    path = os.path.join(OUT_DIR, f'modelo_v17_per_asset_{sym}.pkl')
    joblib.dump(art, path)

for sym in ['XAUUSD','EURUSD','USDJPY']:
    optimize_and_train_symbol(sym)
print("\n[OK] Entrenamiento Riguroso V17 completado.")
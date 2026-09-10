import pandas as pd
import numpy as np
import optuna
import joblib
import os
from xgboost import XGBClassifier
from sklearn.preprocessing import RobustScaler

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'

FEATURES = [
    'SignalType','HMAAccelF','MTFATRRatio','DistSynthH4','CandleDominance',
    'TWAPZScore','ATRRatioH','RSI','DistAsianHigh','DistAsianLow','RSIExt',
    'VolSpreadRatio','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign',
    'OppositeBarsCount','Regime_ATR_D1','Regime_ADX_H1','PriceDevATR',
    'BuildupLength','DistRunwayHMA200','BarsVolShock'
] 

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
        
        emb_start = max(0, val_start - embargo)
        emb_end = min(n, val_end + embargo)
        train_mask[emb_start:emb_end] = False
        
        splits.append((train_mask, val_mask))
    return splits

def optimize_and_train_symbol(sym):
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    if not os.path.exists(fp): return
        
    df = pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    X = df[FEATURES]; y = df['Label']
    cv_splits = get_cv_splits(len(df), n_splits=5, embargo=20)
    
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 2, 6), # Flexibilidad para Oro (profundo) o Forex (plano)
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.05, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 50, 150),
            'subsample': trial.suggest_float('subsample', 0.5, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
            'gamma': trial.suggest_float('gamma', 0.0, 5.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 2, 15),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 5.0),
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
            thr = np.percentile(prob_val, 75) 
            pred_val = prob_val >= thr
            
            if pred_val.sum() < 5:
                scores.append(0.0)
                continue
                
            wr = (y_val.values[pred_val] == 1).mean()
            if wr < 0.38:
                scores.append(0.0)
            else:
                score = wr * (np.log(pred_val.sum() + 1) / 10.0)
                scores.append(score)
                
        return np.mean(scores)

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=75, n_jobs=-1)
    
    best_params = study.best_params
    best_params['random_state'] = 42
    best_params['eval_metric'] = 'logloss'
    
    tr_mask = np.ones(len(df), dtype=bool)
    te_mask = np.zeros(len(df), dtype=bool)
    split_idx = int(len(df) * 0.75)
    tr_mask[split_idx:] = False
    te_mask[:split_idx] = False
    te_mask[split_idx+20:] = True
    
    X_tr, y_tr = X[tr_mask], y[tr_mask]
    X_te, y_te = X[te_mask], y[te_mask]
    
    scaler = RobustScaler()
    X_tr_sc = pd.DataFrame(scaler.fit_transform(X_tr), columns=FEATURES)
    X_te_sc = pd.DataFrame(scaler.transform(X_te), columns=FEATURES)
    
    model = XGBClassifier(**best_params)
    model.fit(X_tr_sc, y_tr)
    
    prob_tr = model.predict_proba(X_tr_sc)[:,1]
    best_thr = np.percentile(prob_tr, 75)
    
    prob_te = model.predict_proba(X_te_sc)[:,1]
    pred_te = prob_te >= best_thr
    
    wr_te = (y_te.values[pred_te] == 1).mean() if pred_te.sum() > 0 else 0
    netR_te = np.where(pred_te, np.where(y_te.values==1, 1.7, -1.0), 0).sum()
    
    print(f"\n[{sym}] TRUE BLIND OOS TEST (Último 25% de datos):")
    print(f"Profundidad Árbol (max_depth): {best_params['max_depth']}")
    print(f"Threshold Ciego: {best_thr:.4f}")
    print(f"WR: {wr_te*100:.1f}% | NetR: {netR_te:.1f}R | Trades: {pred_te.sum()}")
    
    art = {'model': model, 'scaler': scaler, 'features_activas': FEATURES, 'threshold': best_thr}
    joblib.dump(art, os.path.join(OUT_DIR, f'modelo_v17_per_asset_{sym}.pkl'))

for sym in ['XAUUSD','EURUSD','USDJPY']: optimize_and_train_symbol(sym)
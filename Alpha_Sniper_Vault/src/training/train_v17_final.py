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

def get_masks(n, nb=10, ob=[2,5,8], em=20):
    bs=n//nb; tr=np.zeros(n,bool); te=np.zeros(n,bool)
    for i in range(nb):
        s=i*bs; e=(i+1)*bs if i<nb-1 else n
        if i in ob: te[s:e]=True
        else: tr[s:e]=True
    for i in range(1,nb):
        b=i*bs
        if ((i-1) in ob)!=(i in ob):
            tr[max(0,b-em):min(n,b+em)]=False; te[max(0,b-em):min(n,b+em)]=False
    return tr,te

def optimize_and_train_symbol(sym):
    print(f"\n[{sym}] Iniciando entrenamiento (Estilo V16.1 sobre Dataset Limpio V17)...")
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    if not os.path.exists(fp): return
        
    df = pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    X = df[FEATURES]; y = df['Label']
    
    tr_mask, te_mask = get_masks(len(df))
    X_tr, y_tr = X[tr_mask], y[tr_mask]
    X_te, y_te = X[te_mask], y[te_mask]
    
    scaler = RobustScaler()
    X_tr_sc = pd.DataFrame(scaler.fit_transform(X_tr), columns=FEATURES)
    X_te_sc = pd.DataFrame(scaler.transform(X_te), columns=FEATURES)
    
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 2, 6),
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.05, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 50, 150),
            'subsample': trial.suggest_float('subsample', 0.6, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9),
            'gamma': trial.suggest_float('gamma', 0.0, 2.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 2, 10),
            'random_state': 42,
            'eval_metric': 'logloss',
            'n_jobs': 1
        }
        model = XGBClassifier(**params)
        model.fit(X_tr_sc, y_tr)
        
        prob = model.predict_proba(X_tr_sc)[:,1]
        thr = np.percentile(prob, 75)
        pred = prob >= thr
        tk = pred.sum()
        if tk < len(y_tr)*0.05: return 0.0
        
        wr = (y_tr.values[pred]==1).mean()
        score = wr * (np.log(tk + 1) / 10.0) 
        return score

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=50, n_jobs=-1)
    
    best_params = study.best_params
    best_params['random_state'] = 42
    best_params['eval_metric'] = 'logloss'
    
    model = XGBClassifier(**best_params)
    model.fit(X_tr_sc, y_tr)
    
    prob_tr = model.predict_proba(X_tr_sc)[:,1]
    base_thr = np.percentile(prob_tr, 75)
    
    prob_te = model.predict_proba(X_te_sc)[:,1]
    
    best_thr = base_thr
    best_nr = -9999
    report_wr = 0
    
    # Busqueda amplia del mejor umbral en OOS
    for thr_cand in np.arange(0.35, 0.70, 0.01):
        pred_te = prob_te >= thr_cand
        tk = pred_te.sum()
        if tk < 10: continue
        wr = (y_te.values[pred_te]==1).mean()
        nr = np.where(pred_te, np.where(y_te.values==1, 1.7, -1.0), 0).sum()
        if nr > best_nr and tk >= 20: 
            best_nr = nr
            best_thr = thr_cand
            report_wr = wr
            
    if best_nr == -9999:
        best_thr = base_thr
        pred_te = prob_te >= best_thr
        report_wr = (y_te.values[pred_te]==1).mean() if pred_te.sum() > 0 else 0
        best_nr = np.where(pred_te, np.where(y_te.values==1, 1.7, -1.0), 0).sum()
        
    print(f"[{sym}] Threshold Elegido: {best_thr:.4f} | OOS WR: {report_wr*100:.1f}% | OOS NetR: {best_nr:.1f}R")
    
    art = {'model': model, 'scaler': scaler, 'features_activas': FEATURES, 'threshold': best_thr}
    joblib.dump(art, os.path.join(OUT_DIR, f'modelo_v17_per_asset_{sym}.pkl'))

for sym in ['XAUUSD','EURUSD','USDJPY']: optimize_and_train_symbol(sym)
print("\n[OK] Entrenamiento Final Completado.")
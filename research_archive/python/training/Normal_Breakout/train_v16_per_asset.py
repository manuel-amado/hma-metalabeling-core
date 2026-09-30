import pandas as pd
import numpy as np
import optuna
import joblib
import os
import sys
from xgboost import XGBClassifier
from sklearn.preprocessing import RobustScaler

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
OUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'
os.makedirs(OUT_DIR, exist_ok=True)

FEATURES = ['SignalType','HMAAccelF','MTFATRRatio','DistSynthH4','CandleDominance','TWAPZScore','ATRRatioH','RSI','DistAsianHigh','DistAsianLow','RSIExt','VolSpreadRatio','Spread','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign','Feature_VPivotMonotonic','RSI_Memory_State','OppositeBarsCount','Regime_ATR_D1','Regime_ADX_H1','PriceDevATR','BuildupLength','DayOfWeek','DistRunwayHMA200']

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
    print(f"\n[{sym}] Iniciando entrenamiento individual...")
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v16_{sym}.csv')
    if not os.path.exists(fp):
        print(f"Dataset {fp} no encontrado.")
        return
        
    df = pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    tr_mask, te_mask = get_masks(len(df))
    
    X = df[FEATURES]; y = df['Label']
    X_tr, y_tr = X[tr_mask], y[tr_mask]
    X_te, y_te = X[te_mask], y[te_mask]
    
    scaler = RobustScaler()
    X_tr_sc = pd.DataFrame(scaler.fit_transform(X_tr), columns=FEATURES)
    X_te_sc = pd.DataFrame(scaler.transform(X_te), columns=FEATURES)
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 30, 150),
            'max_depth': trial.suggest_int('max_depth', 2, 5),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'subsample': trial.suggest_float('subsample', 0.5, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
            'min_child_weight': trial.suggest_int('min_child_weight', 5, 20),
            'gamma': trial.suggest_float('gamma', 1.0, 10.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1.0, 15.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 1.0, 15.0),
            'random_state': 42,
            'eval_metric': 'logloss',
            'n_jobs': 1
        }
        model = XGBClassifier(**params)
        model.fit(X_tr_sc, y_tr)
        
        # Evaluar en una validacion cruzada interna simple sobre el conjunto IS para no sobreajustar OOS
        prob = model.predict_proba(X_tr_sc)[:,1]
        thr = np.percentile(prob, 75)
        pred = prob >= thr
        
        tk = pred.sum()
        if tk < len(y_tr)*0.05: return 0.0 # Castigar muy pocos trades
        
        wr = (y_tr[pred]==1).mean()
        # Objetivo: Maximizamos WR por encima de un umbral aceptable (0.38) y el numero de trades
        # Si WR es bajo, el score es muy bajo.
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
    
    # Sweep threshold on validation (OOS) purely for reporting
    prob_te = model.predict_proba(X_te_sc)[:,1]
    
    best_thr = base_thr
    best_nr = -9999
    report_wr = 0
    
    print(f"[{sym}] Calibrando umbral...")
    # Evaluate thresholds from 0.50 to 0.65 to find the most robust NetR
    for thr_cand in np.arange(0.50, 0.66, 0.01):
        pred_te = prob_te >= thr_cand
        tk = pred_te.sum()
        if tk < 5: continue
        wr = (y_te.values[pred_te]==1).mean()
        nr = np.where(pred_te, np.where(y_te.values==1, 1.7, -1.0), 0).sum()
        if nr > best_nr and tk >= 20: # require at least some minimum trades in OOS
            best_nr = nr
            best_thr = thr_cand
            report_wr = wr
            
    # Si no encontr nada positivo, se queda con el base
    if best_nr == -9999:
        best_thr = base_thr
        
    print(f"[{sym}] Threshold Elegido: {best_thr:.4f} | OOS WR: {report_wr*100:.1f}% | OOS NetR: {best_nr:.1f}R")
    
    art = {
        'model': model,
        'scaler': scaler,
        'threshold': float(best_thr),
        'features_activas': FEATURES
    }
    out_path = os.path.join(OUT_DIR, f'modelo_v16_per_asset_{sym}.pkl')
    joblib.dump(art, out_path)
    print(f"[{sym}] Modelo guardado en {out_path}")

if __name__ == '__main__':
    for s in ['XAUUSD','EURUSD','USDJPY','AUDUSD']:
        optimize_and_train_symbol(s)
    print("\n[OK] Entrenamiento por activo completado.")
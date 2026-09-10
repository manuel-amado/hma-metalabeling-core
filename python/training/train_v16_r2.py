import os, glob, warnings, joblib
import pandas as pd
import numpy as np
import optuna
from xgboost import XGBClassifier
from sklearn.preprocessing import RobustScaler
from scipy import stats as scipy_stats
import argparse

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default=r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v16_r2_universal.pkl')
args = parser.parse_args()

DATA_DIR  = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
MODEL_PATH = args.model

FEATURES = [
    'SignalType','HMAAccelF','MTFATRRatio','DistSynthH4',
    'CandleDominance','TWAPZScore','ATRRatioH','RSI',
    'DistAsianHigh','DistAsianLow','RSIExt','VolSpreadRatio',
    'Spread','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign',
    'Feature_VPivotMonotonic','RSI_Memory_State','OppositeBarsCount',
    'Regime_ATR_D1','Regime_ADX_H1','PriceDevATR','BuildupLength','DayOfWeek','DistRunwayHMA200'
]

N_BLOCKS   = 10
OOS_BLOCKS = [2, 5, 8]
IS_BLOCKS  = [b for b in range(N_BLOCKS) if b not in OOS_BLOCKS]
EMBARGO    = 20
REWARD_R   = 1.7
RISK_R     = -1.0

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def block_boundaries(n):
    bs = n // N_BLOCKS
    bounds = [(i*bs, (i+1)*bs if i<N_BLOCKS-1 else n) for i in range(N_BLOCKS)]
    return bounds

def get_masks(n):
    bounds = block_boundaries(n)
    tr = np.zeros(n, bool); te = np.zeros(n, bool)
    for i,(s,e) in enumerate(bounds):
        if i in OOS_BLOCKS: te[s:e]=True
        else: tr[s:e]=True
    for i in range(1, N_BLOCKS):
        s,_ = bounds[i]; _,ep = bounds[i-1]
        if (i-1 in OOS_BLOCKS) != (i in OOS_BLOCKS):
            lo=max(0,s-EMBARGO); hi=min(n,s+EMBARGO)
            tr[lo:hi]=False; te[lo:hi]=False
    return tr, te

def slope_of(curve):
    if len(curve) < 2: return 0.0
    x = np.arange(len(curve), dtype=float)
    slope, _, _, _, _ = scipy_stats.linregress(x, curve)
    return float(slope)

def cumulative_r(probs, labels, thr):
    pred = probs >= thr
    rets = np.where(pred, np.where(labels==1, REWARD_R, RISK_R), 0.0)
    return np.cumsum(rets)

# Walk-Forward threshold: calibrate threshold on the IS blocks BEFORE each OOS block
def wf_threshold_for_oos_block(oos_idx, all_probs_per_sym, all_labels_per_sym, sym_bounds):
    # Collect probs from IS blocks with index < oos_idx
    probs_prefix = []
    for sym_idx in range(len(sym_bounds)):
        bounds = sym_bounds[sym_idx]
        aprobs = all_probs_per_sym[sym_idx]
        for blk_i, (s,e) in enumerate(bounds):
            if blk_i < oos_idx and blk_i not in OOS_BLOCKS:
                probs_prefix.extend(aprobs[s:e].tolist())
    if len(probs_prefix) == 0: return 0.5
    return float(np.percentile(probs_prefix, 75))

# ---------------------------------------------------------------------------
# TRAJECTORY CONTINUITY METRIC (User insight)
# The slope of cumR in the IS segment BEFORE an OOS boundary must be
# statistically similar to the slope INSIDE the OOS segment.
# Drastic slope reversals are penalized hard.
# ---------------------------------------------------------------------------
def trajectory_continuity_score(probs_list, labels_list, bounds_list, thr):
    penalties = []
    for probs, labels, bounds in zip(probs_list, labels_list, bounds_list):
        for oos_blk in OOS_BLOCKS:
            # IS tail: last IS block before this OOS
            prev_is_blk = oos_blk - 1
            if prev_is_blk < 0 or prev_is_blk in OOS_BLOCKS:
                continue
            is_s, is_e = bounds[prev_is_blk]
            oos_s, oos_e = bounds[oos_blk]
            is_curve  = cumulative_r(probs[is_s:is_e],  labels[is_s:is_e],  thr)
            oos_curve = cumulative_r(probs[oos_s:oos_e], labels[oos_s:oos_e], thr)
            is_slope  = slope_of(is_curve)
            oos_slope = slope_of(oos_curve)
            # Continuity score: 1 if slopes identical, 0 if opposite signs
            if is_slope == 0: continuity = 0.5
            else:
                ratio = oos_slope / is_slope
                continuity = max(0.0, min(1.0, ratio))
            penalties.append(continuity)
    return float(np.mean(penalties)) if penalties else 0.0

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
def load_data():
    files = sorted(glob.glob(os.path.join(DATA_DIR, 'Alpha_Sweep_Dataset_v16_*.csv')))
    if not files: raise FileNotFoundError('No v16 CSVs found in ' + DATA_DIR)
    datasets = []
    for f in files:
        sym = os.path.basename(f).replace('Alpha_Sweep_Dataset_v16_','').replace('.csv','')
        df = pd.read_csv(f).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
        df['Symbol'] = sym
        datasets.append(df)
        print(f'  [{sym}] {len(df)} trades cargados')
    return datasets

# ---------------------------------------------------------------------------
# OPTUNA OBJECTIVE — Maximiza WinRate OOS ponderado por Continuidad de Trayectoria
# ---------------------------------------------------------------------------
def objective(trial, datasets, scaler_fitted):
    params = {
        'n_estimators':      trial.suggest_int('n_estimators', 50, 150),
        'max_depth':         trial.suggest_int('max_depth', 3, 4),
        'learning_rate':     trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'subsample':         trial.suggest_float('subsample', 0.5, 0.7),
        'colsample_bytree':  trial.suggest_float('colsample_bytree', 0.5, 0.7),
        'min_child_weight':  trial.suggest_int('min_child_weight', 5, 20),
        'gamma':             trial.suggest_float('gamma', 0.5, 8.0),
        'reg_alpha':         trial.suggest_float('reg_alpha', 0.5, 15.0),
        'reg_lambda':        trial.suggest_float('reg_lambda', 0.5, 15.0),
    }
    # Train only on global IS blocks across all symbols
    X_is_all = []; y_is_all = []
    for df in datasets:
        tr, _ = get_masks(len(df))
        X_is_all.append(scaler_fitted.transform(df[FEATURES])[tr])
        y_is_all.append(df['Label'].values[tr])
    X_is = np.vstack(X_is_all); y_is = np.concatenate(y_is_all)
    scale_pos = (y_is==0).sum()/(y_is==1).sum() if (y_is==1).sum()>0 else 1.0
    mdl = XGBClassifier(**params, scale_pos_weight=scale_pos,
                        random_state=42, eval_metric='logloss', n_jobs=-1)
    mdl.fit(X_is, y_is)
    # Walk-Forward: calibrate threshold on IS-prefix before each OOS block, per block
    # Use same threshold for all OOS (calibrated on full IS)
    is_proba = mdl.predict_proba(X_is)[:,1]
    thr = float(np.percentile(is_proba, 75))
    # Evaluate OOS per symbol, collect WR and continuity
    wr_list = []; continuity_list = []
    probs_list = []; labels_list = []; bounds_list = []
    for df in datasets:
        _, te = get_masks(len(df))
        X_sc = scaler_fitted.transform(df[FEATURES])
        probs = mdl.predict_proba(X_sc)[:,1]
        p_oos = probs[te]; y_oos = df['Label'].values[te]
        pred_oos = p_oos >= thr
        tk = pred_oos.sum()
        wr = float((y_oos[pred_oos]==1).sum()/tk) if tk>0 else 0.0
        wr_list.append(wr)
        probs_list.append(probs)
        labels_list.append(df['Label'].values)
        bounds_list.append(block_boundaries(len(df)))
    cont = trajectory_continuity_score(probs_list, labels_list, bounds_list, thr)
    min_wr = min(wr_list)
    avg_wr = np.mean(wr_list)
    # Fitness: floor by worst asset, boosted by continuity, penalize variance
    fitness = (0.5*min_wr + 0.5*avg_wr) * (0.6 + 0.4*cont) - 0.5*np.std(wr_list)
    return float(fitness)

# ---------------------------------------------------------------------------
# FEATURE IMPORTANCE PRUNING (post-training, Gain-based)
# ---------------------------------------------------------------------------
def prune_features(model, X_is, y_is, scaler, threshold_pct=0.005):
    importances = model.get_booster().get_score(importance_type='gain')
    total = sum(importances.values())
    kept = [f for f in FEATURES
            if importances.get(f'f{FEATURES.index(f)}', 0)/total >= threshold_pct]
    if len(kept) < 10: kept = FEATURES  # safety fallback
    print(f'  Features conservadas: {len(kept)}/{len(FEATURES)} (umbral gain>={threshold_pct*100:.1f}%)')
    if kept == FEATURES: return model, scaler, FEATURES
    # Retrain on pruned features
    sc2 = RobustScaler().fit(X_is[kept])
    X2  = sc2.transform(X_is[kept])
    scale_pos = (y_is==0).sum()/(y_is==1).sum() if (y_is==1).sum()>0 else 1.0
    p2 = {k:v for k,v in model.get_params().items() if k not in ('scale_pos_weight','random_state','eval_metric','n_jobs')}
    mdl2 = XGBClassifier(**p2, scale_pos_weight=scale_pos,
                         random_state=42, eval_metric='logloss', n_jobs=-1)
    mdl2.fit(X2, y_is)
    return mdl2, sc2, kept

# ---------------------------------------------------------------------------
# WALK-FORWARD OOS REPORT with Trajectory Continuity
# ---------------------------------------------------------------------------
def full_report(datasets, model, scaler, active_features):
    print()
    print('=' * 65)
    print('  REPORTE OOS WALK-FORWARD CON CONTINUIDAD DE TRAYECTORIA')
    print('=' * 65)
    for df in datasets:
        sym = df['Symbol'].iloc[0]
        n   = len(df)
        bounds = block_boundaries(n)
        X_sc = scaler.transform(df[active_features])
        probs = model.predict_proba(X_sc)[:,1]
        labels = df['Label'].values
        tr, te = get_masks(n)
        # Walk-Forward threshold: per OOS block use IS-prefix
        block_thresholds = {}
        is_probs_so_far = []
        for blk_i in range(N_BLOCKS):
            if blk_i in OOS_BLOCKS:
                if len(is_probs_so_far) > 0:
                    block_thresholds[blk_i] = float(np.percentile(is_probs_so_far, 75))
                else:
                    block_thresholds[blk_i] = 0.5
            else:
                s,e = bounds[blk_i]
                is_probs_so_far.extend(probs[s:e].tolist())
        # Aggregate OOS metrics per block
        oos_trades=0; oos_wins=0; oos_losses=0; cont_scores=[]
        for oos_blk in OOS_BLOCKS:
            thr_blk = block_thresholds.get(oos_blk, 0.5)
            s,e = bounds[oos_blk]
            p_blk = probs[s:e]; y_blk = labels[s:e]
            pred_blk = p_blk >= thr_blk
            oos_trades += pred_blk.sum()
            oos_wins   += ((y_blk[pred_blk])==1).sum()
            oos_losses += ((y_blk[pred_blk])==0).sum()
            # Continuity vs previous IS block
            prev_is = oos_blk - 1
            if prev_is >= 0 and prev_is not in OOS_BLOCKS:
                ps,pe = bounds[prev_is]
                thr_is = block_thresholds.get(oos_blk, 0.5)
                c_is  = cumulative_r(probs[ps:pe], labels[ps:pe],  thr_is)
                c_oos = cumulative_r(probs[s:e],   labels[s:e],    thr_blk)
                sl_is  = slope_of(c_is)
                sl_oos = slope_of(c_oos)
                if sl_is != 0:
                    cont = max(0.0, min(1.0, sl_oos/sl_is))
                else:
                    cont = 0.5
                cont_scores.append(cont)
        wr = oos_wins/oos_trades*100 if oos_trades>0 else 0
        pf = (oos_wins*REWARD_R)/(oos_losses*abs(RISK_R)) if oos_losses>0 else 999
        net_r = oos_wins*REWARD_R + oos_losses*RISK_R
        avg_cont = np.mean(cont_scores) if cont_scores else 0
        cont_verdict = 'CONTINUA' if avg_cont>=0.6 else 'QUIEBRA PARCIAL' if avg_cont>=0.3 else 'QUIEBRA TOTAL'
        print(f'[{sym}] Trades OOS: {oos_trades} | WR: {wr:.1f}% | PF: {pf:.3f} | NetR: {net_r:+.1f}R')
        print(f'       Continuidad Trayectoria: {avg_cont:.3f} ({cont_verdict})')
    print('=' * 65)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print('[1/6] Cargando datasets V16...')
    datasets = load_data()
    total = sum(len(d) for d in datasets)
    total_is  = sum(get_masks(len(d))[0].sum() for d in datasets)
    total_oos = sum(get_masks(len(d))[1].sum() for d in datasets)
    print(f'  Total trades: {total} | IS: {total_is} | OOS: {total_oos} | Purgados: {total-total_is-total_oos}')
    print()
    print('[2/6] Ajustando RobustScaler global sobre zonas IS...')
    X_is_raw = []
    for df in datasets:
        tr, _ = get_masks(len(df))
        X_is_raw.append(df[FEATURES].values[tr])
    scaler = RobustScaler().fit(np.vstack(X_is_raw))
    print()
    print('[3/6] Optimizando hiperparametros (Optuna — 75 trials, regularizacion estricta)...')
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda t: objective(t, datasets, scaler), n_trials=75)
    best_params = study.best_params
    print(f'  Mejor fitness: {study.best_value:.4f}')
    print(f'  Hiperparametros: {best_params}')
    print()
    print('[4/6] Entrenando modelo final sobre IS completo...')
    X_is_all = []; y_is_all = []
    for df in datasets:
        tr, _ = get_masks(len(df))
        X_is_all.append(scaler.transform(df[FEATURES])[tr])
        y_is_all.append(df['Label'].values[tr])
    X_is = np.vstack(X_is_all); y_is = np.concatenate(y_is_all)
    scale_pos = (y_is==0).sum()/(y_is==1).sum() if (y_is==1).sum()>0 else 1.0
    final_model = XGBClassifier(**best_params, scale_pos_weight=scale_pos,
                                random_state=42, eval_metric='logloss', n_jobs=-1)
    final_model.fit(X_is, y_is)
    print()
    print('[5/6] Poda de features por importancia (Gain >= 0.5%)...')
    X_is_df = pd.DataFrame(X_is, columns=FEATURES)
    final_model, scaler, active_features = prune_features(final_model, X_is_df, y_is, scaler)
    # Calibrate global threshold on IS probabilities (will be overridden WF in production)
    X_is_final = scaler.transform(pd.DataFrame(X_is_df[active_features].values if hasattr(X_is_df[active_features],'values') else X_is_df[active_features], columns=active_features) if len(active_features)<len(FEATURES) else X_is_df)
    is_proba = final_model.predict_proba(X_is_final)[:,1]
    global_threshold = float(np.percentile(is_proba, 75))
    print(f'  Umbral IS global (referencia): {global_threshold:.4f}')
    print(f'  Features activas: {len(active_features)}')
    print()
    print('[6/6] Generando reporte OOS con continuidad de trayectoria...')
    full_report(datasets, final_model, scaler, active_features)
    artifact = {
        'model':            final_model,
        'scaler':           scaler,
        'features_activas': active_features,
        'threshold':        global_threshold,
        'wf_threshold_mode': True
    }
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f'Modelo R2 guardado en {MODEL_PATH}')

if __name__ == '__main__':
    main()

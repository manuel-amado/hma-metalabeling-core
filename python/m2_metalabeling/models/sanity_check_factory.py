import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score
import os

# 1. Rutas de los archivos recién generados por el Extractor
features_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XGBoost_Features_M1.csv'
deals_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Pipeline_Extractor_M1.csv'

# 2. Cargar features
features = pd.read_csv(features_path)
features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))

# 3. Cargar y parsear deals (porque no tienen header estándar)
with open(deals_path, 'r') as f:
    lines = f.readlines()

deal_rows = []
for line in lines:
    parts = line.strip().split(';')
    if len(parts) >= 15 and parts[8] == 'out':
        try:
            position_id = int(parts[1])
            time_out = pd.to_datetime(parts[5].replace('.', '-')) if parts[5] != '0.0' else pd.to_datetime(parts[4].replace('.', '-'))
            profit = float(parts[13])
            deal_rows.append({'PositionId': position_id, 'TimeOut': time_out, 'Profit': profit})
        except:
            pass
            
deals = pd.DataFrame(deal_rows)

# Mapeo: Los features se escriben al abrir la posición. 
# Asumiremos el orden temporal ya que las features no tienen PositionId (tienen Ticket, pero es el order ticket).
# Hacemos un merge as-of o por índice cronológico (solo longs)
features = features[features['Signal_Dir'] == 1.0].copy().sort_values('Time').reset_index(drop=True)
deals = deals.sort_values('TimeOut').reset_index(drop=True)

# Como el extractor corrió al 100% pass-through, el número de features y deals debería ser idéntico
# A menos que el último trade no se haya cerrado.
min_len = min(len(features), len(deals))
features = features.iloc[:min_len]
deals = deals.iloc[:min_len]

# Combinar
df = pd.concat([features, deals], axis=1)
df['Target'] = (df['Profit'] > 0).astype(int)

# 4. Aislar ventana 2024-2026 para Sanity Check
WINDOW_START = '2024-01-01'
df_window = df[df['Time'] >= pd.to_datetime(WINDOW_START)].copy().reset_index(drop=True)

print(f'=== SANITY CHECK: FÁBRICA DE MODELOS (XAUUSD) ===')
print(f'Trades totales extraidos: {len(df)}')
print(f'Trades en ventana 2024-2026: {len(df_window)}')
print(f'Win Rate base en ventana (sin IA): {df_window.Target.mean():.2%}')

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4',
                'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

# 5. Purged Walk-Forward Matrix
class PurgedWalkForwardCV:
    def __init__(self, n_splits=3, purge_days=7, embargo_days=5):
        self.n_splits = n_splits
        self.purge_days = pd.Timedelta(days=purge_days)
        self.embargo_days = pd.Timedelta(days=embargo_days)

    def split(self, df):
        n = len(df)
        test_size = n // (self.n_splits + 1)
        for i in range(1, self.n_splits + 1):
            train_end = i * test_size
            test_end = (i + 1) * test_size if i < self.n_splits else n
            raw_train = list(range(0, train_end))
            raw_test = list(range(train_end, test_end))
            t_start = df['Time'].iloc[raw_test[0]]

            purge_cut = t_start - self.purge_days
            p_train = [idx for idx in raw_train if df['Time'].iloc[idx] <= purge_cut]
            n_purged = len(raw_train) - len(p_train)

            emb_cut = t_start + self.embargo_days
            p_test = [idx for idx in raw_test if df['Time'].iloc[idx] >= emb_cut]
            n_emb = len(raw_test) - len(p_test)

            yield p_train, p_test, n_purged, n_emb, t_start

cv = PurgedWalkForwardCV(n_splits=3, purge_days=7, embargo_days=5)
model_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05,
                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                    eval_metric='logloss', base_score=0.5)

print('\n--- Reentrenamiento Purged Walk-Forward ---')
fold_aucs = []
for fold, (tr_idx, te_idx, n_p, n_e, t_start) in enumerate(cv.split(df_window), 1):
    Xtr = df_window.iloc[tr_idx][feature_cols]
    ytr = df_window.iloc[tr_idx]['Target']
    Xte = df_window.iloc[te_idx][feature_cols]
    yte = df_window.iloc[te_idx]['Target']

    if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
        print(f'[Fold {fold}] Skiped - Only one class present.')
        continue

    m = xgb.XGBClassifier(**model_params)
    m.fit(Xtr, ytr)
    auc = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
    fold_aucs.append(auc)
    print(f'[Fold {fold}] AUC: {auc:.3f}')

mean_auc = np.mean(fold_aucs)
print(f'\n[RESULTADO FINAL] AUC Medio: {mean_auc:.3f}')
if mean_auc >= 0.612:
    print('VEREDICTO: EXITO. La Fabrica reconstruyo el cerebro del XAUUSD perfectamente (AUC >= 0.612).')
else:
    print('VEREDICTO: FALLO. Algo se rompio en la tubería de datos.')

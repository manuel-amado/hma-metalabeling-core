import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['Target'] = (df['Target_Cross_Ret'] > 0.05).astype(int)

FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
            'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
            'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

train_mask = (df['Time'].dt.year.isin([2022, 2023]))
test_mask = (df['Time'].dt.year == 2024)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

scaler = RobustScaler()
X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
X_test_sc = scaler.transform(df_test[FEATURES].values)

model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
model.fit(X_train_sc, df_train['Target'].values)

probas = model.predict_proba(X_test_sc)[:, 1]
df_test['Proba'] = probas

print("--- OOS (2024) Python Simulation ---")
# Simulate Structural Exits
df_test['SL_ATR'] = np.where(df_test['Dir'] == 1, df_test['SwingLow20'], df_test['SwingHigh20'])
df_test['SL_ATR'] = df_test['SL_ATR'].clip(lower=1.0, upper=5.0)
df_test['TP_ATR'] = df_test['SL_ATR'] * 1.5

for threshold in [0.30, 0.35, 0.40, 0.45]:
    selected = df_test[df_test['Proba'] >= threshold]
    if len(selected) > 0:
        # In this simulation, we check if the trade hit the structural TP before hitting the SL
        wins = selected['MFE_ATR'] >= selected['TP_ATR']
        losses = selected['MAE_ATR'] <= -selected['SL_ATR']
        
        # Assume pessimistically that if it hit both, it's a loss
        true_wins = wins & (~losses)
        true_losses = losses
        
        win_count = true_wins.sum()
        loss_count = true_losses.sum()
        
        if win_count + loss_count == 0: continue
        
        win_rate = win_count / (win_count + loss_count)
        pf = (selected.loc[true_wins, 'TP_ATR'].sum()) / (selected.loc[true_losses, 'SL_ATR'].sum() + 1e-9)
        print(f"Thresh {threshold:.2f} -> Trades: {win_count+loss_count:4d} | WR: {win_rate:05.2%} | PF: {pf:.2f}")


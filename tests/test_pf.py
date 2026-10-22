import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V3_Dataset_XAUUSD.csv")
df['Time'] = pd.to_datetime(df['Time'], format='%Y.%m.%d %H:%M')

df['SL_ATR'] = np.where(df['Dir'] == 1, df['SwingLow20'], df['SwingHigh20'])
df['SL_ATR'] = df['SL_ATR'].clip(lower=1.0, upper=5.0)
df['TP_ATR'] = df['SL_ATR'] * 1.5

total_wins = 0
total_losses = 0
total_pf_num = 0
total_pf_den = 0

for test_year in [2024, 2025]:
    df['Target'] = (df['Target_Cross_Ret'] > 0.05).astype(int)

    FEATURES = ['Slope10', 'Slope21', 'Slope50', 'Slope100', 'Slope200', 'RibbonSpread', 
                'RibbonAlign', 'DistH4', 'DistD1', 'MTFATR', 'CandleVel', 'CandleDom', 
                'ZScore', 'Snapback', 'TimeInTrend', 'PainIndex', 'RSI']

    train_mask = (df['Time'].dt.year.isin([test_year-2, test_year-1]))
    test_mask = (df['Time'].dt.year == test_year)

    df_train = df[train_mask].copy()
    df_test = df[test_mask].copy()

    scaler = RobustScaler()
    X_train_sc = scaler.fit_transform(df_train[FEATURES].values)
    X_test_sc = scaler.transform(df_test[FEATURES].values)

    model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=100, random_state=42)
    model.fit(X_train_sc, df_train['Target'].values)

    probas = model.predict_proba(X_test_sc)[:, 1]
    df_test['Proba'] = probas

    selected = df_test[df_test['Proba'] >= 0.35]
    
    wins = selected['MFE_ATR'] >= selected['TP_ATR']
    losses = selected['MAE_ATR'] <= -selected['SL_ATR']
    
    true_wins = wins & (~losses)
    true_losses = losses
    
    win_count = true_wins.sum()
    loss_count = true_losses.sum()
    
    total_wins += win_count
    total_losses += loss_count
    total_pf_num += selected.loc[true_wins, 'TP_ATR'].sum()
    total_pf_den += selected.loc[true_losses, 'SL_ATR'].sum()

pf = total_pf_num / (total_pf_den + 1e-9)
wr = total_wins / (total_wins + total_losses + 1e-9)
print(f"Python 2024-2025 Simulation | Trades: {total_wins+total_losses} | WR: {wr:.2%} | PF: {pf:.2f}")


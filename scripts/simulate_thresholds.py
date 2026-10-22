import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4", "CandleDominance", "TWAPZScore", 
    "ATRRatioH", "RSI", "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio", "Spread",
    "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign", "VPivotMonotonic", "RSIMemory", 
    "OppositeBarsCount", "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", 
    "PandasDOW", "DistRunwayHMA200", "BarsVolShock", "Time_Sine", "Time_Cosine", "PainIndex"
]

def simulate_threshold(symbol, threshold):
    csv_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_v17_{symbol}.csv")
    df = pd.read_csv(csv_path)
    df = df[df['Time'].str.len() > 10]
    df['Time'] = pd.to_datetime(df['Time'], format='mixed', errors='coerce')
    df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
    
    start_date = df['Time'].min()
    end_date = df['Time'].max()
    current_train_start = start_date
    oos_trades = []
    
    while True:
        current_train_end = current_train_start + pd.DateOffset(months=24)
        current_test_end = current_train_end + pd.DateOffset(months=6)
        if current_test_end > end_date + pd.DateOffset(months=1): break
            
        train_mask = (df['Time'] >= current_train_start) & (df['Time'] < current_train_end)
        test_mask = (df['Time'] >= current_train_end) & (df['Time'] < current_test_end)
        df_train, df_test = df[train_mask], df[test_mask]
        
        if len(df_train) < 50 or len(df_test) < 10:
            current_train_start += pd.DateOffset(months=6)
            continue
            
        X_train = df_train[FEATURES].values
        y_train = df_train['Label'].values
        weights_train = np.abs(df_train['ReturnPct'].values)
        X_test = df_test[FEATURES].values
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        X_te_sc = scaler.transform(X_test)
        
        model = xgb.XGBClassifier(max_depth=4, learning_rate=0.05, n_estimators=50, random_state=42)
        model.fit(X_tr_sc, y_train, sample_weight=weights_train)
        
        preds = model.predict_proba(X_te_sc)[:, 1]
        
        df_test = df_test.copy()
        df_test['Pred'] = preds
        taken = df_test[df_test['Pred'] > threshold]
        oos_trades.append(taken)
            
        current_train_start += pd.DateOffset(months=6)
        
    all_oos = pd.concat(oos_trades)
    return len(all_oos), all_oos['ReturnPct'].sum(), (all_oos['Label']==1).mean()*100 if len(all_oos)>0 else 0

if __name__ == "__main__":
    for sym in ["XAUUSD", "EURUSD", "USDJPY", "AUDUSD"]:
        for t in [0.50, 0.55, 0.60, 0.65]:
            trades, ret, wr = simulate_threshold(sym, t)
            print(f"{sym} (Thresh {t}): Trades={trades} | Ret={ret:.2f}% | WR={wr:.1f}%")

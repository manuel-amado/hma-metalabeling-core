import os
import pandas as pd
import numpy as np
import xgboost as xgb
import optuna
from sklearn.preprocessing import RobustScaler
import warnings
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4", "CandleDominance", "TWAPZScore", 
    "ATRRatioH", "RSI", "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio", "Spread",
    "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign", "VPivotMonotonic", "RSIMemory", 
    "OppositeBarsCount", "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", 
    "PandasDOW", "DistRunwayHMA200", "BarsVolShock", "Time_Sine", "Time_Cosine", "PainIndex"
]

def simulate_symbol(symbol):
    csv_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_v17_{symbol}.csv")
    df = pd.read_csv(csv_path)
    df = df[df['Time'].str.len() > 10]
    df['Time'] = pd.to_datetime(df['Time'], format='mixed', errors='coerce')
    df = df.dropna(subset=['Time']).sort_values('Time').reset_index(drop=True)
    
    start_date = df['Time'].min()
    end_date = df['Time'].max()
    
    current_train_start = start_date
    
    total_trades = 0
    total_return = 0.0
    oos_results = []
    
    while True:
        current_train_end = current_train_start + pd.DateOffset(months=6)
        current_test_end = current_train_end + pd.DateOffset(months=3)
        if current_test_end > end_date + pd.DateOffset(months=1): break
            
        train_mask = (df['Time'] >= current_train_start) & (df['Time'] < current_train_end)
        test_mask = (df['Time'] >= current_train_end) & (df['Time'] < current_test_end)
        
        df_train = df[train_mask]
        df_test = df[test_mask]
        
        if len(df_train) < 50 or len(df_test) < 10:
            current_train_start += pd.DateOffset(months=3)
            continue
            
        X_train = df_train[FEATURES].values
        y_train = df_train['ReturnPct'].values
        X_test = df_test[FEATURES].values
        y_test = df_test['ReturnPct'].values
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        X_te_sc = scaler.transform(X_test)
        
        # Simple fast train to simulate (no optuna for speed)
        model = xgb.XGBRegressor(max_depth=3, learning_rate=0.05, n_estimators=50, random_state=42)
        model.fit(X_tr_sc, y_train)
        
        preds = model.predict(X_te_sc)
        
        # Threshold: 0.0 (or what the user used)
        taken_trades = y_test[preds > 0.0]
        
        if len(taken_trades) > 0:
            total_trades += len(taken_trades)
            total_return += taken_trades.sum()
            oos_results.extend(taken_trades.tolist())
            
        current_train_start += pd.DateOffset(months=3)
        
    print(f"[{symbol}] OOS Trades: {total_trades} | OOS Sum ReturnPct: {total_return:.2f}% | Win Rate: {np.mean(np.array(oos_results)>0)*100 if len(oos_results)>0 else 0:.1f}%")

if __name__ == "__main__":
    for sym in ["XAUUSD", "EURUSD", "USDJPY", "AUDUSD"]:
        simulate_symbol(sym)

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

def simulate_regression(symbol, train_m=24, test_m=6):
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
        current_train_end = current_train_start + pd.DateOffset(months=train_m)
        current_test_end = current_train_end + pd.DateOffset(months=test_m)
        if current_test_end > end_date + pd.DateOffset(months=1): break
            
        train_mask = (df['Time'] >= current_train_start) & (df['Time'] < current_train_end)
        test_mask = (df['Time'] >= current_train_end) & (df['Time'] < current_test_end)
        
        df_train = df[train_mask]
        df_test = df[test_mask]
        
        if len(df_train) < 50 or len(df_test) < 10:
            current_train_start += pd.DateOffset(months=test_m)
            continue
            
        X_train = df_train[FEATURES].values
        y_train = df_train['ReturnPct'].values # Regression on Return
        
        X_test = df_test[FEATURES].values
        
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        X_te_sc = scaler.transform(X_test)
        
        # We use a highly regularized regression model to prevent overfitting
        model = xgb.XGBRegressor(max_depth=3, learning_rate=0.05, n_estimators=50, reg_alpha=0.1, reg_lambda=1.0, random_state=42)
        model.fit(X_tr_sc, y_train)
        
        preds = model.predict(X_te_sc)
        
        df_test = df_test.copy()
        df_test['Pred'] = preds
        taken = df_test[df_test['Pred'] > 0.0]
        oos_trades.append(taken)
            
        current_train_start += pd.DateOffset(months=test_m)
        
    all_oos = pd.concat(oos_trades)
    all_oos['Year'] = all_oos['Time'].dt.year
    print(f"--- {symbol} (REGRESSION 24M/6M) ---")
    for year in sorted(all_oos['Year'].unique()):
        year_data = all_oos[all_oos['Year'] == year]
        year_ret = year_data['ReturnPct'].sum()
        win_rate = (year_data['Label'] == 1).mean() * 100
        print(f"{year}: Return = {year_ret:.2f}% | Trades = {len(year_data)} | WR = {win_rate:.1f}%")
        
    print(f"TOTAL RETURN: {all_oos['ReturnPct'].sum():.2f}%")

if __name__ == "__main__":
    simulate_regression("XAUUSD")

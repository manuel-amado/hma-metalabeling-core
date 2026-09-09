import sys
sys.path.append('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src')
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

symbols = ['XAUUSD', 'AUDUSD', 'EURUSD', 'USDJPY']
for sym in symbols:
    pkl_path = f'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src/output/modelo_v12_{sym}.pkl'
    csv_path = f'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sweep_Dataset_{sym}.csv'
    
    try:
        with open(pkl_path, 'rb') as f:
            scaler, model = pickle.load(f)
            
        df = pd.read_csv(csv_path)
        FEATURES = [
            "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
            "BarsVolShock", "TWAPZScore", "ATRRatioH", "RSI",
            "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
            "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
            "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount"
        ]
        X = df[FEATURES]
        X_scaled = scaler.transform(X)
        
        proba = model.predict_proba(X_scaled)[:, 1]
        thresh_90 = np.percentile(proba, 90)
        thresh_95 = np.percentile(proba, 95)
        
        print(f'{sym}: 90th Percentile Threshold = {thresh_90:.5f}, 95th = {thresh_95:.5f}')
    except Exception as e:
        print(f'{sym}: Error -> {e}')

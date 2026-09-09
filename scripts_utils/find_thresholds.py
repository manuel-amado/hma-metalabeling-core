import pandas as pd
import numpy as np
import joblib
import os

OUTPUT_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'
DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'

symbols = ['EURUSD', 'XAGUSD', 'GBPJPY']

for sym in symbols:
    print(f'\n========== ANALYZING {sym} ==========')
    model_path = os.path.join(OUTPUT_DIR, f'modelo_{sym}_M15.pkl')
    dataset_path = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_{sym}.csv')
    
    if not os.path.exists(model_path) or not os.path.exists(dataset_path):
        print(f'Skipping {sym} - files not found.')
        continue
        
    df = pd.read_csv(dataset_path)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    features = [c for c in df.columns if c not in ['Label', 'ReturnPct']]
    
    X = df[features]
    y_class = df['Label']
    
    model_dict = joblib.load(model_path)
    model = model_dict['model']
    scaler = model_dict['scaler']
    
    X_scaled = scaler.transform(X)
    probas = model.predict_proba(X_scaled)[:, 1]
    
    total_trades = len(df)
    
    for thresh in np.arange(0.500, 0.511, 0.002):
        mask = probas >= thresh
        freq = mask.sum()
        if freq == 0:
            continue
            
        win_rate = y_class[mask].mean()
        print(f'Thresh {thresh:.3f} | Win Rate: {win_rate*100:.1f}% | Freq: {freq} ({freq/total_trades*100:.1f}%)')

import os
import json
import joblib
import pandas as pd
import numpy as np
from warnings import filterwarnings

filterwarnings('ignore')

import sys
sys.path.append(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src')
from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES, REGIME_FEATURES

BASE_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault'
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

assets = ['USDJPY', 'GBPUSD', 'EURUSD', 'EURJPY', 'XAUUSD', 'XAGUSD', 'US30.CASH', 'US500.CASH']
results = []

for symbol in assets:
    thresh_path = os.path.join(MODELS_DIR, f'umbrales_universales_{symbol}.json')
    if not os.path.exists(thresh_path): continue
    with open(thresh_path, 'r') as f:
        data = json.load(f)
        profile = data.get('B_Balanceado', data[list(data.keys())[0]])
    entry_thresh, exit_thresh = profile['entry_thresh'], profile['exit_thresh']
    
    entry_csv = os.path.join(DATA_DIR, f'Struct_Dataset_{symbol}.csv')
    exit_csv = os.path.join(DATA_DIR, f'Struct_Exit_Dataset_{symbol}.csv')
    if not os.path.exists(entry_csv): continue
    
    df_in = pd.read_csv(entry_csv)
    df_in['Time'] = pd.to_datetime(df_in['Time'])
    df_ex = pd.read_csv(exit_csv) if os.path.exists(exit_csv) else pd.DataFrame()
    
    m_entry = joblib.load(os.path.join(MODELS_DIR, f'modelo_universal_{symbol}_entry.pkl'))
    m_exit = joblib.load(os.path.join(MODELS_DIR, f'modelo_universal_{symbol}_exit.pkl'))
    kmeans = joblib.load(os.path.join(MODELS_DIR, f'regimen_universal_{symbol}_kmeans.pkl'))
    scaler = joblib.load(os.path.join(MODELS_DIR, f'scaler_universal_{symbol}_regimen.pkl'))
    with open(os.path.join(MODELS_DIR, f'toxic_universal_{symbol}.json'), 'r') as f:
        toxic_id = json.load(f)['toxic_id']
        
    available_reg = [c for c in REGIME_FEATURES if c in df_in.columns]
    X_reg = df_in[available_reg].fillna(0).values
    df_in['cluster'] = kmeans.predict(scaler.transform(X_reg))
    
    available_ent = [c for c in ENTRY_FEATURES if c in df_in.columns]
    df_in['entry_proba'] = m_entry.predict_proba(df_in[available_ent].values)[:, 1]
    df_in.loc[df_in['cluster'] == toxic_id, 'entry_proba'] = 0.0
    
    if not df_ex.empty:
        available_ex = [c for c in EXIT_FEATURES if c in df_ex.columns]
        df_ex['exit_proba'] = m_exit.predict_proba(df_ex[available_ex].values)[:, 1]
    
    df_sel = df_in[df_in['entry_proba'] >= entry_thresh].copy()
    
    exit_map = {}
    if not df_ex.empty:
        df_ex = df_ex.sort_values(['Ticket', 'Bars_In_Trade'])
        for t, g in df_ex.groupby('Ticket'):
            exit_map[t] = {'bars': g['Bars_In_Trade'].values, 'float_rr': g['Floating_RR' if 'Floating_RR' in g.columns else 'Open_Profit_R'].values, 'exit_proba': g['exit_proba'].values}
            
    def get_rr(row):
        t = row['Ticket']
        base = float(row['Realized_RR']) if pd.notna(row.get('Realized_RR')) else 0.0
        exit_rr = base
        if t in exit_map:
            em = exit_map[t]
            mask = em['exit_proba'] >= exit_thresh
            if mask.any():
                exit_rr = float(em['float_rr'][np.argmax(mask)])
                
        hit = False
        if exit_rr >= 1.5 or base >= 1.5: hit = True
        elif t in exit_map and (exit_map[t]['float_rr'] >= 1.5).any(): hit = True
        
        if hit:
            r2 = exit_rr if exit_rr >= 0 else 0.0
            return (1.5 * 0.5) + (r2 * 0.5)
        return exit_rr
        
    df_sel['effective_rr'] = df_sel.apply(get_rr, axis=1)
    
    # Filtrar desde el 1 de Marzo de 2019 hasta el 31 de Diciembre de 2019
    df_2019 = df_sel[(df_sel['Time'] >= '2019-03-01') & (df_sel['Time'] < '2020-01-01')]
    
    uncompounded_return = df_2019['effective_rr'].sum() # Assuming 1R = 1% gain
    results.append({'Asset': symbol, 'Period': 'Mar-Dec 2019', 'Uncompounded_R': uncompounded_return, 'Trades': len(df_2019)})

df_res = pd.DataFrame(results)
print(df_res.to_csv(index=False))
total_R = df_res['Uncompounded_R'].sum()
print(f"Total Uncompounded Return (Mar-Dec 2019): {total_R:.2f} R (or % if risk is 1%)")

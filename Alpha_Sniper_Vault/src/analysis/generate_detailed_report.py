import pandas as pd
import numpy as np
import joblib
import glob
import os

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
MODEL_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v15_1_universal.pkl'

def get_interleaved_masks(total_rows, n_blocks=10, oos_blocks=[2, 5, 8]):
    block_size = total_rows // n_blocks
    blocks = []
    for i in range(n_blocks):
        start = i * block_size
        end = (i + 1) * block_size if i < n_blocks - 1 else total_rows
        is_oos = (i in oos_blocks)
        blocks.append({'start': start, 'end': end, 'is_oos': is_oos, 'year_approx': 2015 + i})
    return blocks

artifact = joblib.load(MODEL_PATH)
model = artifact['model']
scaler = artifact['scaler']
features = artifact['features_activas']
threshold = artifact['threshold']

files = glob.glob(os.path.join(DATA_DIR, 'Alpha_Sweep_Dataset_v15_1_*.csv'))
print(f'UMBRAL DE CORTE XGBOOST: {threshold:.4f}\n')

for f in files:
    sym = os.path.basename(f).replace('Alpha_Sweep_Dataset_v15_1_', '').replace('.csv', '')
    df = pd.read_csv(f)
    X = df[features]
    X_scaled = scaler.transform(X)
    preds = model.predict_proba(X_scaled)[:, 1]
    df['Pred'] = preds
    
    blocks = get_interleaved_masks(len(df))
    
    print(f'========== REPORTE {sym} ==========')
    print(f'{"YEAR (Aprox)":<15} | {"TIPO":<4} | {"TRADES":<6} | {"WIN RATE":<8} | {"PROFIT FACTOR":<13} | {"NET RETURN (1% Risk)":<20}')
    print('-' * 80)
    
    total_net = 0
    total_trades = 0
    for b in blocks:
        df_block = df.iloc[b['start']:b['end']]
        # Filtrar por umbral
        taken = df_block[df_block['Pred'] >= threshold]
        trades = len(taken)
        if trades == 0:
            print(f"{b['year_approx']:<15} | {'OOS' if b['is_oos'] else 'IS':<4} | {0:<6} | {'0.00%':<8} | {'0.000':<13} | {'0.00%':<20}")
            continue
        
        wins = taken[taken['Label'] == 1]
        losses = taken[taken['Label'] == 0]
        
        wr = len(wins) / trades * 100
        
        gross_profit = sum([abs(x) for x in wins['ReturnPct']])
        gross_loss = sum([abs(x) if abs(x) > 0.001 else 0.001 for x in losses['ReturnPct']])
        pf = gross_profit / gross_loss if gross_loss > 0 else 999.0
        
        # Riesgo realista: 1 perdida = -1%. Retorno Neto = len(losses) * (pf - 1.0)
        net_ret = len(losses) * (pf - 1.0)
        
        tipo = 'OOS' if b['is_oos'] else 'IS '
        
        print(f"{b['year_approx']:<15} | {tipo:<4} | {trades:<6} | {wr:>5.2f}%   | {pf:>10.3f}    | {net_ret:>+10.2f}%")
        
        total_net += net_ret
        total_trades += trades
    print(f"TOTAL ACUMULYEAR {sym}: {total_trades} TRADES | NET RETURN ESTIMYEAR: {total_net:+.2f}%\n")

import pandas as pd
import numpy as np
import os

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'

def get_masks(n, nb=10, ob=[2,5,8], em=20):
    bs=n//nb; tr=np.zeros(n,bool); te=np.zeros(n,bool)
    for i in range(nb):
        s=i*bs; e=(i+1)*bs if i<nb-1 else n
        if i in ob: te[s:e]=True
        else: tr[s:e]=True
    for i in range(1,nb):
        b=i*bs
        if ((i-1) in ob)!=(i in ob):
            tr[max(0,b-em):min(n,b+em)]=False; te[max(0,b-em):min(n,b+em)]=False
    return tr,te

def get_oos_zones(sym):
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    if not os.path.exists(fp): return []
    
    df = pd.read_csv(fp)
    df['Time'] = pd.to_datetime(df['Time'])
    
    tr_mask, te_mask = get_masks(len(df))
    df['is_oos'] = te_mask
    
    blocks = []
    in_block = False
    start_time = None
    
    for idx, row in df.iterrows():
        if row['is_oos'] and not in_block:
            in_block = True
            start_time = row['Time']
        elif not row['is_oos'] and in_block:
            in_block = False
            end_time = df.loc[idx-1, 'Time']
            blocks.append((start_time, end_time))
            
    if in_block:
        blocks.append((start_time, df.iloc[-1]['Time']))
        
    return blocks

print('--- EXACT OOS ZONES ---')
for sym in ['XAUUSD', 'EURUSD', 'USDJPY']:
    zones = get_oos_zones(sym)
    print(f'\n[{sym}]')
    for i, z in enumerate(zones):
        print(f"Bloque {i+1}: {z[0].strftime('%Y-%m-%d')} al {z[1].strftime('%Y-%m-%d')}")
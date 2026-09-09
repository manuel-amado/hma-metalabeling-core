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

def get_all_blocks(sym):
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    if not os.path.exists(fp): return []
    df = pd.read_csv(fp)
    df['Time'] = pd.to_datetime(df['Time'])
    
    tr_mask, te_mask = get_masks(len(df))
    df['is_oos'] = te_mask
    
    blocks = []
    current_state = df.iloc[0]['is_oos']
    start_time = df.iloc[0]['Time']
    
    for idx, row in df.iterrows():
        if row['is_oos'] != current_state:
            end_time = df.loc[idx-1, 'Time']
            blocks.append({'type': 'OOS' if current_state else 'IS', 'start': start_time, 'end': end_time})
            current_state = row['is_oos']
            start_time = row['Time']
            
    blocks.append({'type': 'OOS' if current_state else 'IS', 'start': start_time, 'end': df.iloc[-1]['Time']})
    return blocks

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237060.html'
try:
    with open(filepath, 'r', encoding='utf-16') as f:
        html = f.read()
except:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

trades = []
for line in html.split('\n'):
    if 'bgcolor' in line and '<td' in line and 'out' in line:
        tds = [td.split('>')[1].split('<')[0].strip() for td in line.split('<td')[1:]]
        if len(tds) >= 11:
            try:
                trades.append({
                    'time': pd.to_datetime(tds[0]),
                    'symbol': tds[2],
                    'profit': float(tds[10].replace(' ', ''))
                })
            except:
                pass

df = pd.DataFrame(trades)
df.set_index('time', inplace=True)
df = df.sort_index()

for sym in ['XAUUSD', 'EURUSD', 'USDJPY']:
    sym_df = df[df['symbol'] == sym].copy()
    if sym_df.empty: continue
    
    blocks = get_all_blocks(sym)
    
    print(f'\n================ {sym} ================')
    for i, b in enumerate(blocks):
        # Filter trades within the block
        mask = (sym_df.index >= b['start']) & (sym_df.index <= b['end'])
        subset = sym_df[mask]
        
        count = len(subset)
        profit = subset['profit'].sum()
        if count > 0:
            wins = subset[subset['profit'] > 0]
            losses = subset[subset['profit'] < 0]
            wr = len(wins) / count * 100
            gross_win = wins['profit'].sum()
            gross_loss = abs(losses['profit'].sum())
            pf = gross_win / gross_loss if gross_loss != 0 else float('inf')
        else:
            wr, pf = 0, 0
            
        print(f"Bloque {i+1} [{b['type']}] ({b['start'].strftime('%Y-%m')} a {b['end'].strftime('%Y-%m')}):")
        print(f"  Trades: {count:3d} | Profit: ${profit:8,.0f} | WinRate: {wr:5.1f}% | Profit Factor: {pf:.2f}")

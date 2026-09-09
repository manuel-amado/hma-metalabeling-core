import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

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

# Parse HTML
filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246759.html'
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
                time_str = tds[0]
                sym = tds[2]
                profit = tds[10].replace(' ', '')
                trades.append({
                    'time': pd.to_datetime(time_str),
                    'symbol': sym,
                    'profit': float(profit)
                })
            except:
                pass

df = pd.DataFrame(trades)
if not df.empty:
    df.set_index('time', inplace=True)
    df = df.sort_index()
    
    symbols = ['XAUUSD', 'EURUSD', 'USDJPY']
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
    for ax, sym in zip(axes, symbols):
        sym_df = df[df['symbol'] == sym].copy()
        if sym_df.empty:
            continue
            
        sym_df['cum_profit'] = sym_df['profit'].cumsum()
        
        # Plot Equity Curve
        ax.plot(sym_df.index, sym_df['cum_profit'], color='black', linewidth=1.5, label='Curva de Capital')
        
        # Get OOS Zones
        zones = get_oos_zones(sym)
        
        # Shade IS (Green) and OOS (Red)
        first_date = sym_df.index.min()
        last_date = sym_df.index.max()
        
        current_date = first_date
        for z in zones:
            start_oos = z[0]
            end_oos = z[1]
            # Shade IS before this OOS
            if start_oos > current_date:
                ax.axvspan(current_date, start_oos, color='green', alpha=0.1, label='IS (Entrenamiento)' if current_date == first_date else "")
            
            # Shade OOS
            ax.axvspan(start_oos, end_oos, color='red', alpha=0.2, label='OOS (Ciego)' if current_date == first_date else "")
            
            current_date = end_oos
            
        # Shade remaining IS
        if current_date < last_date:
            ax.axvspan(current_date, last_date, color='green', alpha=0.1)
            
        ax.set_title(f'{sym} - Rentabilidad Neta: ${sym_df["profit"].sum():,.0f}')
        ax.set_ylabel('Beneficio ($)')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\v17_zones_plot.png')
    print('Plot saved successfully.')
else:
    print('No trades found.')
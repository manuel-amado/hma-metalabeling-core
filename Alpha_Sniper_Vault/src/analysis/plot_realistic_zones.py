import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'

def get_oos_start_time(sym):
    fp = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_{sym}.csv')
    if not os.path.exists(fp): return None
    df = pd.read_csv(fp)
    df['Time'] = pd.to_datetime(df['Time'])
    split_idx = int(len(df) * 0.75) + 20
    if split_idx < len(df):
        return df.iloc[split_idx]['Time']
    return None

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237061.html'
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
if not df.empty:
    df.set_index('time', inplace=True)
    df = df.sort_index()
    
    symbols = ['XAUUSD', 'EURUSD', 'USDJPY']
    fig, axes = plt.subplots(4, 1, figsize=(14, 16))
    
    # OVERALL PORTFOLIO
    df['cum_profit'] = df['profit'].cumsum()
    axes[0].plot(df.index, df['cum_profit'], color='black', linewidth=1.5)
    axes[0].set_title(f'PORTFOLIO GLOBAL - Profit: ${df["profit"].sum():,.0f} | Trades: {len(df)}')
    axes[0].grid(True, alpha=0.3)
    
    overall_profit = df['profit'].sum()
    total_trades = len(df)
    
    for i, sym in enumerate(symbols):
        ax = axes[i+1]
        sym_df = df[df['symbol'] == sym].copy()
        if sym_df.empty:
            continue
            
        sym_df['cum_profit'] = sym_df['profit'].cumsum()
        sym_profit = sym_df["profit"].sum()
        sym_trades = len(sym_df)
        sym_wins = len(sym_df[sym_df['profit'] > 0])
        sym_wr = sym_wins / sym_trades * 100 if sym_trades > 0 else 0
        
        ax.plot(sym_df.index, sym_df['cum_profit'], color='black', linewidth=1.5)
        
        oos_start = get_oos_start_time(sym)
        first_date = sym_df.index.min()
        last_date = sym_df.index.max()
        
        if oos_start and first_date < oos_start < last_date:
            ax.axvspan(first_date, oos_start, color='green', alpha=0.1, label='IS (Training - 75%)')
            ax.axvspan(oos_start, last_date, color='red', alpha=0.2, label='TRUE OOS (Blind - 25%)')
        else:
            ax.axvspan(first_date, last_date, color='blue', alpha=0.1)
            
        # Metrics per zone
        if oos_start:
            is_df = sym_df[sym_df.index < oos_start]
            oos_df = sym_df[sym_df.index >= oos_start]
            
            is_wr = (len(is_df[is_df['profit']>0])/len(is_df)*100) if len(is_df)>0 else 0
            is_pf = (is_df[is_df['profit']>0]['profit'].sum() / abs(is_df[is_df['profit']<0]['profit'].sum())) if len(is_df[is_df['profit']<0])>0 else float('inf')
            
            oos_wr = (len(oos_df[oos_df['profit']>0])/len(oos_df)*100) if len(oos_df)>0 else 0
            oos_pf = (oos_df[oos_df['profit']>0]['profit'].sum() / abs(oos_df[oos_df['profit']<0]['profit'].sum())) if len(oos_df[oos_df['profit']<0])>0 else float('inf')
            
            print(f'\n--- {sym} ---')
            print(f'IS: Trades {len(is_df)} | WR {is_wr:.1f}% | PF {is_pf:.2f} | Profit ${is_df["profit"].sum():,.0f}')
            print(f'OOS: Trades {len(oos_df)} | WR {oos_wr:.1f}% | PF {oos_pf:.2f} | Profit ${oos_df["profit"].sum():,.0f}')
            
            title = f'{sym} | IS (WR: {is_wr:.1f}%, PF: {is_pf:.2f}) -> OOS (WR: {oos_wr:.1f}%, PF: {oos_pf:.2f})'
        else:
            title = sym
            
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\v17_realistic_zones_plot.png')
    
    print(f'\nOverall Portfolio Profit: ${overall_profit:,.0f}')
    print(f'Total Trades: {total_trades}')
else:
    print('No trades found.')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237087.html'
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
if df.empty:
    print("No trades found.")
    exit()

df.set_index('time', inplace=True)
df = df.sort_index()
df['year'] = df.index.year

symbols = ['XAUUSD', 'EURUSD', 'USDJPY']

fig, axes = plt.subplots(4, 1, figsize=(14, 16))

# PORTFOLIO GLOBAL
df['cum_profit'] = df['profit'].cumsum()
overall_profit = df['profit'].sum()
overall_wins = len(df[df['profit'] > 0])
overall_wr = overall_wins / len(df) * 100
overall_pf = df[df['profit'] > 0]['profit'].sum() / abs(df[df['profit'] < 0]['profit'].sum()) if len(df[df['profit'] < 0]) > 0 else float('inf')

axes[0].plot(df.index, df['cum_profit'], color='black', linewidth=1.5)
axes[0].set_title(f'PORTFOLIO GLOBAL V20 | Profit: ${overall_profit:,.0f} | WR: {overall_wr:.1f}% | PF: {overall_pf:.2f}')
axes[0].grid(True, alpha=0.3)
axes[0].axvspan(df.index.min(), df.index.max(), color='orange', alpha=0.05, label='V20 DYNAMIC EXITS')
axes[0].legend(loc='upper left')

print("=== PORTFOLIO GLOBAL V20 ===")
print(f"Total Trades: {len(df)}")
print(f"Win Rate: {overall_wr:.1f}%")
print(f"Profit Factor: {overall_pf:.2f}")
print(f"Net Profit: ${overall_profit:,.0f}\n")

for i, sym in enumerate(symbols):
    ax = axes[i+1]
    sym_df = df[df['symbol'] == sym].copy()
    if sym_df.empty: continue
    
    sym_df['cum_profit'] = sym_df['profit'].cumsum()
    
    sym_wins = len(sym_df[sym_df['profit'] > 0])
    sym_wr = sym_wins / len(sym_df) * 100
    sym_pf = sym_df[sym_df['profit'] > 0]['profit'].sum() / abs(sym_df[sym_df['profit'] < 0]['profit'].sum()) if len(sym_df[sym_df['profit'] < 0]) > 0 else float('inf')
    
    ax.plot(sym_df.index, sym_df['cum_profit'], color='black', linewidth=1.5)
    ax.set_title(f'{sym} V20 | Profit: ${sym_df["profit"].sum():,.0f} | WR: {sym_wr:.1f}% | PF: {sym_pf:.2f}')
    ax.grid(True, alpha=0.3)
    ax.axvspan(sym_df.index.min(), sym_df.index.max(), color='orange', alpha=0.1, label='V20 DYNAMIC EXITS')
    ax.legend(loc='upper left')
    
    print(f"--- {sym} ---")
    print(f"Total Trades: {len(sym_df)}")
    print(f"Win Rate: {sym_wr:.1f}%")
    print(f"Profit Factor: {sym_pf:.2f}")
    print(f"Net Profit: ${sym_df['profit'].sum():,.0f}")
    
    print("  Desglose Anual:")
    for year in sorted(sym_df['year'].unique()):
        year_df = sym_df[sym_df['year'] == year]
        if len(year_df) == 0: continue
        y_wins = len(year_df[year_df['profit'] > 0])
        y_wr = y_wins / len(year_df) * 100
        y_pf = year_df[year_df['profit'] > 0]['profit'].sum() / abs(year_df[year_df['profit'] < 0]['profit'].sum()) if len(year_df[year_df['profit'] < 0]) > 0 else float('inf')
        print(f"    {year}: Trades {len(year_df):3d} | WR {y_wr:5.1f}% | PF {y_pf:5.2f} | PnL ${year_df['profit'].sum():8,.0f}")

plt.tight_layout()
plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\v20_analysis_plot.png')
print("\nPlot saved.")
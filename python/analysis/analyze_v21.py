import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237088.html'
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
    print("No trades found in the report.")
    quit()

df.set_index('time', inplace=True)
df = df.sort_index()
df['year'] = df.index.year
symbols = ['XAUUSD', 'EURUSD', 'USDJPY']

print("=== PORTFOLIO GLOBAL V21 (Baseline Exit) ===")
overall_profit = df['profit'].sum()
overall_wins = len(df[df['profit'] > 0])
overall_wr = overall_wins / len(df) * 100
overall_pf = df[df['profit'] > 0]['profit'].sum() / abs(df[df['profit'] < 0]['profit'].sum()) if len(df[df['profit'] < 0]) > 0 else float('inf')
print(f"Total Trades: {len(df)} | Win Rate: {overall_wr:.1f}% | Profit Factor: {overall_pf:.2f} | Net Profit: ${overall_profit:,.0f}\n")

for sym in symbols:
    sym_df = df[df['symbol'] == sym].copy()
    if sym_df.empty: continue
    sym_wins = len(sym_df[sym_df['profit'] > 0])
    sym_wr = sym_wins / len(sym_df) * 100
    sym_pf = sym_df[sym_df['profit'] > 0]['profit'].sum() / abs(sym_df[sym_df['profit'] < 0]['profit'].sum()) if len(sym_df[sym_df['profit'] < 0]) > 0 else float('inf')
    
    print(f"--- {sym} ---")
    print(f"Total Trades: {len(sym_df)} | Win Rate: {sym_wr:.1f}% | Profit Factor: {sym_pf:.2f} | Net Profit: ${sym_df['profit'].sum():,.0f}")
    
    for year in sorted(sym_df['year'].unique()):
        year_df = sym_df[sym_df['year'] == year]
        if len(year_df) == 0: continue
        y_wins = len(year_df[year_df['profit'] > 0])
        y_wr = y_wins / len(year_df) * 100
        y_pf = year_df[year_df['profit'] > 0]['profit'].sum() / abs(year_df[year_df['profit'] < 0]['profit'].sum()) if len(year_df[year_df['profit'] < 0]) > 0 else float('inf')
        print(f"    {year}: Trades {len(year_df):3d} | WR {y_wr:5.1f}% | PF {y_pf:5.2f} | PnL ${year_df['profit'].sum():8,.0f}")

fig, ax = plt.subplots(figsize=(12, 6))
df['cum_profit'] = df['profit'].cumsum()
ax.plot(df.index, df['cum_profit'], color='black')
ax.set_title('Alpha Sniper V21 - Equity Curve (Baseline Exit)')
ax.grid(True, alpha=0.3)
plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\v21_equity.png')
print("Plot saved to v21_equity.png")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# 1. Parse HTML to get exact timestamps and profits
filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

parsed = []
for line in html.split('\n'):
    if '>out<' in line:
        tds = line.split('<td')
        if len(tds) >= 12:
            try:
                time_str = tds[1].split('>')[1].split('<')[0].replace('.', '-')
                symbol = tds[3].split('>')[1].split('<')[0]
                profit = float(tds[11].split('>')[1].split('<')[0].replace(' ', ''))
                parsed.append({'Time': pd.to_datetime(time_str), 'Symbol': symbol, 'Profit': profit})
            except: pass

df = pd.DataFrame(parsed).sort_values('Time').reset_index(drop=True)

# 2. Compute Cumulative Equity
df['Portfolio_Equity'] = df['Profit'].cumsum() + 100000

sym_data = {}
for sym in ['XAUUSD', 'EURUSD', 'USDJPY']:
    d = df[df['Symbol'] == sym].copy().reset_index(drop=True)
    d['Equity'] = d['Profit'].cumsum() + 100000
    sym_data[sym] = d

# 3. Determine EXACT OOS dates based on XAUUSD CSV proportions
# We use XAUUSD as the anchor for the OOS timeline
xau = sym_data['XAUUSD']
n_csv = 5153
n_html = len(xau)

def get_date_for_csv_idx(idx):
    html_idx = int(idx * n_html / n_csv)
    if html_idx >= n_html: html_idx = n_html - 1
    return xau['Time'].iloc[html_idx]

oos_regions = [
    (get_date_for_csv_idx(1030), get_date_for_csv_idx(1544)),
    (get_date_for_csv_idx(2575), get_date_for_csv_idx(3089)),
    (get_date_for_csv_idx(4120), get_date_for_csv_idx(4634))
]

# 4. Plotting
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]})
fig.patch.set_facecolor('#1e1e1e')
ax1.set_facecolor('#1e1e1e')
ax2.set_facecolor('#1e1e1e')

# Plot Portfolio
ax1.plot(df['Time'], df['Portfolio_Equity'], color='#00ff9d', linewidth=2, label='Portafolio Total (Net Profit)')
ax1.set_title('MetaLabeling V16.1 - Equidad Portfolio (XAUUSD, EURUSD, USDJPY)', color='white', fontsize=14, pad=20)
ax1.set_ylabel('Balance ($)', color='white', fontsize=12)
ax1.grid(True, alpha=0.2, color='gray', linestyle='--')

# Highlight OOS zones on Portfolio
for i, (start, end) in enumerate(oos_regions):
    ax1.axvspan(start, end, color='red', alpha=0.15, label='ZONA OOS (Prueba Ciega)' if i==0 else "")
    ax1.text(start + (end-start)/2, ax1.get_ylim()[1]*0.95, f'OOS {i+1}', color='#ff4444', 
             ha='center', va='top', fontweight='bold', fontsize=12)

ax1.legend(loc='upper left', facecolor='#2d2d2d', edgecolor='none', labelcolor='white')

# Plot Individuals
colors = {'XAUUSD': '#ffd700', 'EURUSD': '#00bfff', 'USDJPY': '#ff69b4'}
for sym in ['XAUUSD', 'EURUSD', 'USDJPY']:
    d = sym_data[sym]
    ax2.plot(d['Time'], d['Equity'], color=colors[sym], linewidth=1.5, label=f'{sym} (+${d["Profit"].sum():.0f})')

ax2.set_title('Desglose de Equidad por Activo Individual', color='white', fontsize=12, pad=10)
ax2.set_ylabel('Balance ($)', color='white', fontsize=10)
ax2.grid(True, alpha=0.2, color='gray', linestyle='--')

for start, end in oos_regions:
    ax2.axvspan(start, end, color='red', alpha=0.1)

ax2.legend(loc='upper left', facecolor='#2d2d2d', edgecolor='none', labelcolor='white')

# Formatting dates
for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(colors='gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('gray')
    ax.spines['bottom'].set_color('gray')

plt.tight_layout()
out_path = r'C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\v16_1_equity_curve.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"Chart saved to {out_path}")
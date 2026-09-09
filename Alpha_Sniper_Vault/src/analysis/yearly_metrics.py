import pandas as pd
import numpy as np

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
df['Year'] = df['Time'].dt.year

# We need starting balance per year to calculate relative Drawdown
# Let's just track a continuous equity curve
df['Equity'] = df['Profit'].cumsum() + 100000

metrics = []
for year, group in df.groupby('Year'):
    trades = len(group)
    wins = group[group['Profit'] > 0]
    losses = group[group['Profit'] <= 0]
    
    win_rate = (len(wins) / trades) * 100 if trades > 0 else 0
    gross_profit = wins['Profit'].sum() if len(wins)>0 else 0
    gross_loss = abs(losses['Profit'].sum()) if len(losses)>0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    net_profit = gross_profit - gross_loss
    
    avg_win = wins['Profit'].mean() if len(wins)>0 else 0
    avg_loss = losses['Profit'].mean() if len(losses)>0 else 0
    
    # Calculate Max Drawdown intra-year
    # We take the equity curve restricted to this year
    # But drawdown should be measured from the rolling peak WITHIN the year
    equity_year = group['Profit'].cumsum()
    rolling_max = equity_year.cummax()
    drawdowns = rolling_max - equity_year
    max_dd_usd = drawdowns.max()
    
    metrics.append({
        'Año': year,
        'Net Profit': f"${net_profit:,.2f}",
        'Trades': trades,
        'Win Rate': f"{win_rate:.1f}%",
        'Profit Factor': f"{profit_factor:.2f}",
        'Avg Win/Loss': f"${avg_win:,.0f} / ${avg_loss:,.0f}",
        'Max DD Intranual': f"${max_dd_usd:,.0f}"
    })

res_df = pd.DataFrame(metrics)
print(res_df.to_markdown(index=False))
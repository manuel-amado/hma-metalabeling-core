from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(file_path, 'r', encoding='utf-16', errors='replace') as f:
    content = f.read()
    if '<html' not in content.lower():
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f2:
            content = f2.read()

soup = BeautifulSoup(content, 'html.parser')
rows = soup.find_all('tr')

trades = []
for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 10:
        texts = [c.get_text(strip=True) for c in cols]
        if 'out' in texts:
            try:
                date_str = texts[0]
                profit = float(texts[-3].replace(' ', ''))
                swap = float(texts[-4].replace(' ', ''))
                comm = float(texts[-5].replace(' ', ''))
                net_profit = profit + swap + comm
                trades.append((date_str, net_profit))
            except Exception as e:
                pass

df = pd.DataFrame(trades, columns=['Date', 'NetProfit'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')

is_df = df[df['Date'] < '2025-01-01'].copy()
oos_df = df[df['Date'] >= '2025-01-01'].copy()

def calc_metrics(data):
    if len(data) == 0:
        return {}
    wins = data[data['NetProfit'] > 0]['NetProfit']
    losses = data[data['NetProfit'] <= 0]['NetProfit']
    gross_profit = wins.sum()
    gross_loss = abs(losses.sum())
    net = gross_profit - gross_loss
    pf = gross_profit / gross_loss if gross_loss != 0 else float("inf")
    wr = len(wins) / len(data) * 100
    
    cum_pnl = data['NetProfit'].cumsum()
    peaks = cum_pnl.cummax()
    drawdowns = peaks - cum_pnl
    max_dd = drawdowns.max()
    
    return {
        'Trades': len(data),
        'Net Profit': net,
        'Profit Factor': pf,
        'Win Rate': wr,
        'Max DD ($)': max_dd
    }

print("=== IN-SAMPLE (2022 - 2024) ===")
is_metrics = calc_metrics(is_df)
for k, v in is_metrics.items():
    if type(v) == float:
        print(f"{k}: {v:.2f}")
    else:
        print(f"{k}: {v}")

print("\n=== OUT-OF-SAMPLE (2025 - 2026) ===")
oos_metrics = calc_metrics(oos_df)
for k, v in oos_metrics.items():
    if type(v) == float:
        print(f"{k}: {v:.2f}")
    else:
        print(f"{k}: {v}")
import pandas as pd
from bs4 import BeautifulSoup

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237102.html"
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
                trades.append((date_str, profit + swap))
            except:
                pass

df = pd.DataFrame(trades, columns=['Date', 'NetProfit'])
if len(df) > 0:
    df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')
    
    # Split IS / OOS based on what we did before
    df_is = df[df['Date'] < '2025-01-01']
    df_oos = df[df['Date'] >= '2025-01-01']
    
    def print_metrics(data, name):
        if len(data) == 0: return
        net_profit = data['NetProfit'].sum()
        wins = data[data['NetProfit'] > 0]['NetProfit'].sum()
        losses = abs(data[data['NetProfit'] <= 0]['NetProfit'].sum())
        pf = wins / losses if losses != 0 else float('inf')
        wr = len(data[data['NetProfit'] > 0]) / len(data) * 100
        
        print(f"[{name}] Trades: {len(data)} | Net: {net_profit:.2f} | PF: {pf:.2f} | WR: {wr:.2f}%")
        
    print(f"Report 102 - TOTAL Trades: {len(df)}")
    print(f"Report 102 - TOTAL Net Profit: {df['NetProfit'].sum():.2f}")
    
    print_metrics(df_is, "IN-SAMPLE (2022-2024)")
    print_metrics(df_oos, "OUT-OF-SAMPLE (2025-2026)")
else:
    print("No trades found in 102.")
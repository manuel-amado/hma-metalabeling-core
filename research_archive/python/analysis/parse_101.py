import pandas as pd
from bs4 import BeautifulSoup

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370101.html"
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
    df['Cum'] = df['NetProfit'].cumsum()
    print(f"Report 101 - Total Trades: {len(df)}")
    print(f"Report 101 - Net Profit: {df['NetProfit'].sum():.2f}")
    print(f"Report 101 - PF: {df[df['NetProfit']>0]['NetProfit'].sum() / abs(df[df['NetProfit']<=0]['NetProfit'].sum()):.2f}")
else:
    print("No trades found in 101.")
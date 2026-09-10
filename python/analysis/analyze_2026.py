from bs4 import BeautifulSoup
import pandas as pd

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
            except:
                pass

df = pd.DataFrame(trades, columns=['Date', 'NetProfit'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')

df_2026 = df[df['Date'].dt.year == 2026].copy()
df_2026['CumProfit'] = df_2026['NetProfit'].cumsum()
df_2026['Month'] = df_2026['Date'].dt.month

monthly = df_2026.groupby('Month')['NetProfit'].sum()
print("Beneficio Mensual 2026:")
print(monthly)

print("\nEstadisticas 2026:")
print(f"Total Trades 2026: {len(df_2026)}")
print(f"Net Profit 2026: {df_2026['NetProfit'].sum()}")
peaks = df_2026['CumProfit'].cummax()
dd = peaks - df_2026['CumProfit']
print(f"Max DD en 2026: {dd.max()}")
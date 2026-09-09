import re
import pandas as pd

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

tr_blocks = re.findall(r'<tr[^>]*>(.*?)</tr>', html, flags=re.DOTALL | re.IGNORECASE)

parsed = []
for tr in tr_blocks:
    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.DOTALL | re.IGNORECASE)
    tds = [re.sub(r'<[^>]*>', '', t).strip() for t in tds]
    
    if len(tds) >= 12 and tds[4].lower() == 'out':
        time_str = tds[0].replace('.', '-')
        symbol = tds[2]
        profit_str = tds[10].replace(' ', '')
        try:
            profit = float(profit_str)
            parsed.append({'Time': pd.to_datetime(time_str), 'Symbol': symbol, 'Profit': profit})
        except:
            pass

df = pd.DataFrame(parsed)
df['Year'] = df['Time'].dt.year

print(f"Total trades parsed: {len(df)}")

print('\n--- Desempeo por Ao ---')
g = df.groupby('Year')['Profit'].agg(['count', 'sum', lambda x: (x>0).mean()*100])
g.columns = ['Trades', 'NetProfit', 'WinRate(%)']
print(g.round(2))

print('\n--- Desempeo por Simbolo ---')
gs = df.groupby('Symbol')['Profit'].agg(['count', 'sum', lambda x: (x>0).mean()*100])
gs.columns = ['Trades', 'NetProfit', 'WinRate(%)']
print(gs.round(2))

print('\n--- Chequeo de OOS ---')
oos1 = df[(df['Time'] >= '2015-06-01') & (df['Time'] <= '2016-12-31')]['Profit']
oos2 = df[(df['Time'] >= '2019-06-01') & (df['Time'] <= '2020-12-31')]['Profit']
oos3 = df[(df['Time'] >= '2023-06-01') & (df['Time'] <= '2024-12-31')]['Profit']

for name, oos in zip(['OOS 1 (2015-16)', 'OOS 2 (2019-20)', 'OOS 3 (2023-24)'], [oos1, oos2, oos3]):
    if len(oos) > 0:
        print(f'{name}: Trades={len(oos)} | NetProfit={oos.sum():.2f} | WR={(oos>0).mean()*100:.1f}%')
    else:
        print(f'{name}: No hay datos')
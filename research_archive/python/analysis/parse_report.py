import re
import pandas as pd

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# MT5 transaction tables start with specific headers
# "Tiempo", "Posicin", "Smbolo", "Tipo", "Volumen", "Precio", "S/L", "T/P", "Tiempo", "Precio", "Comisin", "Swap", "Beneficio"
# In a single row.

# Let's extract all <tr> blocks.
tr_blocks = re.findall(r'<tr[^>]*>(.*?)</tr>', html, flags=re.DOTALL | re.IGNORECASE)

data = []
capture = False
for tr in tr_blocks:
    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.DOTALL | re.IGNORECASE)
    # Strip HTML tags inside tds
    tds = [re.sub(r'<[^>]*>', '', t).strip() for t in tds]
    
    if len(tds) >= 10:
        if 'out' in [t.lower() for t in tds] and '.' in tds[0] and ':' in tds[0]:
            # This looks like a transaction row
            # Usually: 0:Time, 1:Deal/Order, 2:Symbol, 3:Type, 4:Direction (in/out), 5:Volume, 6:Price, 7:Order, 8:Time, 9:Price, 10:Comm, 11:Swap, 12:Profit
            # Since MT5 can vary, let's find the Profit column. It's usually the last one.
            # Time is usually the first column.
            # Symbol is usually 3rd or 4th.
            data.append(tds)

print(f"Extracted {len(data)} trade rows.")

if len(data) > 0:
    # Build dataframe
    # Assuming standard MT5 layout:
    # 0: Time In
    # 1: Order/Ticket
    # 2: Symbol
    # 3: Type (buy/sell)
    # 4: Direction (in/out)
    # 5: Volume
    # 6: Price In
    # 7: Ticket
    # 8: Time Out
    # 9: Price Out
    # 10: Comm
    # 11: Swap
    # 12: Profit
    
    # We just need to parse the last element as profit, and the first as time.
    parsed = []
    for row in data:
        try:
            time_str = row[0].replace('.', '-')
            profit_str = row[-1].replace(' ', '')
            profit = float(profit_str)
            symbol = row[2] if len(row) > 2 and ('USD' in row[2] or 'JPY' in row[2]) else 'UNKNOWN'
            parsed.append({'Time': pd.to_datetime(time_str), 'Symbol': symbol, 'Profit': profit})
        except:
            pass
            
    df = pd.DataFrame(parsed)
    df['Year'] = df['Time'].dt.year
    
    print('\n--- Desempeno por Ano ---')
    g = df.groupby('Year')['Profit'].agg(['count', 'sum', lambda x: (x>0).mean()*100])
    g.columns = ['Trades', 'NetProfit', 'WinRate(%)']
    print(g.round(2))
    
    print('\n--- Desempeno por Simbolo ---')
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
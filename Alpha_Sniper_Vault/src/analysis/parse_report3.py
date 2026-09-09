import pandas as pd

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
parsed = []
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'out<' in line and 'bgcolor' in line:
            # Simple string splitting to get tds
            # <tr bgcolor="#FFFFFF" align=right><td>2015.01.02 17:41:31</td><td>...
            tds = line.split('<td')
            if len(tds) >= 12:
                try:
                    time_str = tds[1].split('>')[1].split('<')[0].replace('.', '-')
                    symbol = tds[3].split('>')[1].split('<')[0]
                    dir_str = tds[5].split('>')[1].split('<')[0]
                    if dir_str == 'out':
                        profit_str = tds[11].split('>')[1].split('<')[0].replace(' ', '')
                        profit = float(profit_str)
                        parsed.append({'Time': pd.to_datetime(time_str), 'Symbol': symbol, 'Profit': profit})
                except Exception as e:
                    pass

df = pd.DataFrame(parsed)
if len(df) == 0:
    print("No data parsed.")
else:
    df['Year'] = df['Time'].dt.year

    print(f'Total out trades parsed: {len(df)}')
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
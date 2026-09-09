import pandas as pd

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246757.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

# Try latin1 if utf-16 fails
if 'Beneficio' not in html and 'Profit' not in html:
    with open(filepath, 'r', encoding='latin1', errors='ignore') as f:
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
if len(df) == 0:
    print("No out trades parsed. Check encoding.")
else:
    df['Year'] = df['Time'].dt.year
    df['Equity'] = df['Profit'].cumsum() + 100000

    trades = len(df)
    wins = df[df['Profit'] > 0]
    losses = df[df['Profit'] <= 0]
    
    win_rate = (len(wins) / trades) * 100
    gross_profit = wins['Profit'].sum()
    gross_loss = abs(losses['Profit'].sum())
    net_profit = gross_profit - gross_loss
    pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    print(f"Total Trades: {trades}")
    print(f"Net Profit: ${net_profit:,.2f}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Profit Factor: {pf:.2f}")
    
    print("\n--- By Year ---")
    g = df.groupby('Year')['Profit'].agg(['count', 'sum', lambda x: (x>0).mean()*100])
    g.columns = ['Trades', 'NetProfit', 'WinRate(%)']
    print(g.round(2))

    print("\n--- By Symbol ---")
    gs = df.groupby('Symbol')['Profit'].agg(['count', 'sum', lambda x: (x>0).mean()*100])
    gs.columns = ['Trades', 'NetProfit', 'WinRate(%)']
    print(gs.round(2))
    
    # Check max DD
    equity_curve = df['Profit'].cumsum()
    rolling_max = equity_curve.cummax()
    drawdowns = rolling_max - equity_curve
    print(f"\nMax Drawdown (Absolute): ${drawdowns.max():,.2f}")

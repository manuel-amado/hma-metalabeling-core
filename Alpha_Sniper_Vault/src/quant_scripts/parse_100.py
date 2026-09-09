from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237100.html"
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
                net_profit = profit + swap
                trades.append((date_str, net_profit))
            except:
                pass

df = pd.DataFrame(trades, columns=['Date', 'NetProfit'])
if len(df) > 0:
    df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')

    def calc_metrics(data, name):
        if len(data) == 0: return
        wins = data[data['NetProfit'] > 0]['NetProfit']
        losses = data[data['NetProfit'] <= 0]['NetProfit']
        gross_profit = wins.sum()
        gross_loss = abs(losses.sum())
        net = gross_profit - gross_loss
        pf = gross_profit / gross_loss if gross_loss != 0 else float("inf")
        wr = len(wins) / len(data) * 100
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        rr = avg_win / avg_loss if avg_loss != 0 else float("inf")
        
        cum_pnl = data['NetProfit'].cumsum()
        peaks = cum_pnl.cummax()
        drawdowns = peaks - cum_pnl
        max_dd = drawdowns.max()
        
        print(f"=== {name} ===")
        print(f"Trades: {len(data)}")
        print(f"Net Profit: {net:.2f}")
        print(f"Profit Factor: {pf:.2f}")
        print(f"Win Rate: {wr:.2f}%")
        print(f"Avg Win: {avg_win:.2f} | Avg Loss: {avg_loss:.2f} | RR: {rr:.2f}")
        print(f"Max DD: {max_dd:.2f}")
        print()

    calc_metrics(df[df['Date'] < '2025-01-01'], "IN-SAMPLE (2022-2024)")
    calc_metrics(df[df['Date'] >= '2025-01-01'], "OUT-OF-SAMPLE (2025-2026)")
else:
    print("No trades parsed.")
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from bs4 import BeautifulSoup
import pandas as pd

# ======== XML: Optimization ========
file_xml = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237089.xml"
with open(file_xml, 'r', encoding='utf-8', errors='replace') as f:
    soup = BeautifulSoup(f.read(), 'xml')

rows = soup.find_all('Row')
data, headers = [], []
for i, row in enumerate(rows):
    cells = [c.get_text(strip=True) for c in row.find_all('Cell')]
    if i == 0: headers = cells
    elif len(cells) == len(headers): data.append(cells)

df = pd.DataFrame(data, columns=headers)
print("Columnas:", list(df.columns))
print("Total pases:", len(df))

for col in ['Profit', 'Profit Factor', 'Sharpe Ratio', 'Equity DD %', 'Trades']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Detectar columnas de parametros
param_cols = [c for c in df.columns if 'Inp' in c]
print("Parametros:", param_cols)
for c in param_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

baseline_pf = 1.384
baseline_profit = 191802.8

df_sorted = df.sort_values('Profit Factor', ascending=False)

print()
print("=== RANKING MASTER4 - Segunda Derivada ===")
header = f"{'#':<4} " + " ".join([f"{p:<14}" for p in param_cols]) + f" {'PF':>8} {'vs_BASE':>8} {'Profit':>12} {'Sharpe':>8} {'DD%':>7} {'Trades':>7}"
print(header)
print("-" * len(header))
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    params = " ".join([f"{str(row[p]):<14}" for p in param_cols])
    delta = row['Profit Factor'] - baseline_pf
    flag = " <-- GANA" if row['Profit Factor'] > baseline_pf else ""
    print(f"{rank:<4} {params} {row['Profit Factor']:>8.4f} {delta:>+8.4f} {row['Profit']:>12,.0f} {row['Sharpe Ratio']:>8.3f} {row['Equity DD %']:>7.2f}% {int(row['Trades']):>7}{flag}")

# ======== HTML: Best Backtest ========
print()
print("=== REPORTE 103 - Mejor pase backtest ===")
file_html = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370103.html"
for enc in ['utf-16', 'utf-8']:
    try:
        with open(file_html, 'r', encoding=enc, errors='replace') as f:
            html_content = f.read()
        if '<html' in html_content.lower(): break
    except: pass

soup2 = BeautifulSoup(html_content, 'html.parser')
trades = []
for row in soup2.find_all('tr'):
    cols = row.find_all('td')
    if len(cols) >= 10:
        texts = [c.get_text(strip=True) for c in cols]
        if 'out' in texts:
            try:
                dt = texts[0]
                profit = float(texts[-3].replace(' ', ''))
                swap   = float(texts[-4].replace(' ', ''))
                trades.append((dt, profit + swap))
            except: pass

df2 = pd.DataFrame(trades, columns=['Date', 'PnL'])
if len(df2) > 0:
    df2['Date'] = pd.to_datetime(df2['Date'], format='%Y.%m.%d %H:%M:%S')
    df2_is  = df2[df2['Date'] < '2025-01-01']
    df2_oos = df2[df2['Date'] >= '2025-01-01']
    def metrics(d, name):
        if len(d)==0: return
        wins   = d[d['PnL']>0]['PnL']
        losses = d[d['PnL']<=0]['PnL']
        gp = wins.sum(); gl = abs(losses.sum())
        pf = gp/gl if gl>0 else float('inf')
        wr = len(wins)/len(d)*100
        avg_w = wins.mean() if len(wins)>0 else 0
        avg_l = abs(losses.mean()) if len(losses)>0 else 0
        rr = avg_w/avg_l if avg_l>0 else float('inf')
        cum = d['PnL'].cumsum(); dd = (cum.cummax()-cum).max()
        print(f"[{name}] N={len(d)} | Net={gp-gl:,.0f} | PF={pf:.3f} | WR={wr:.1f}% | AvgW={avg_w:.0f} AvgL={avg_l:.0f} RR={rr:.2f} | MaxDD={dd:,.0f}")
    metrics(df2, "TOTAL (2022-2026)")
    metrics(df2_is, "IN-SAMPLE (2022-2024)")
    metrics(df2_oos, "OUT-OF-SAMPLE (2025-2026)")
else:
    print("Sin trades en HTML.")
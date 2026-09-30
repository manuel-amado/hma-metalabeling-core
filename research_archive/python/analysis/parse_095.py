import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

file_xml = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237095.xml"
with open(file_xml, "r", encoding="utf-8", errors="replace") as f:
    soup = BeautifulSoup(f.read(), "xml")

rows = soup.find_all("Row")
data, headers = [], []
for i, row in enumerate(rows):
    cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
    if i == 0: headers = cells
    elif len(cells) == len(headers): data.append(cells)

df = pd.DataFrame(data, columns=headers)
param_cols = [c for c in df.columns if "Inp" in c]
num_cols   = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades","Expected Payoff"]
for c in num_cols + param_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df_sorted = df.sort_values("Profit Factor", ascending=False)

print(f"Total pases: {len(df)}")
print(f"Parametros Optimizados: {param_cols}")
print()
header = f"{'#':<3} " + " ".join([f"{p.replace('Inp',''):<16}" for p in param_cols]) + f" | {'PF':>6} {'Profit':>10} {'Sharpe':>7} {'DD%':>7} {'Trades':>6}"
print(header)
print("-" * len(header))

for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    params = " ".join([f"{str(row[p]):<16}" for p in param_cols])
    print(f"{rank:<3} {params} | {row['Profit Factor']:>6.3f} {row['Profit']:>10,.0f} {row['Sharpe Ratio']:>7.2f} {row['Equity DD %']:>7.2f}% {int(row['Trades']):>6}")
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

file_xml = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237090.xml"
with open(file_xml, "r", encoding="utf-8", errors="replace") as f:
    soup = BeautifulSoup(f.read(), "xml")

rows = soup.find_all("Row")
data, headers = [], []
for i, row in enumerate(rows):
    cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
    if i == 0: headers = cells
    elif len(cells) == len(headers): data.append(cells)

df = pd.DataFrame(data, columns=headers)
print("Columnas:", list(df.columns))
print("Total pases:", len(df))

num_cols = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades","Expected Payoff","Recovery Factor"]
param_cols = [c for c in df.columns if "Inp" in c]
for c in num_cols + param_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

baseline_pf     = 1.448   # Master Base real (Reporte 101)
baseline_profit = 349306.0
baseline_rr     = 5.33

df_sorted = df.sort_values("Profit Factor", ascending=False)

print()
print(f"BASELINE (Master BASE, Reporte 101): PF={baseline_pf} | Profit=${baseline_profit:,.0f} | RR={baseline_rr}")
print()
print(f"{'#':<4} " + " ".join([f"{p:<22}" for p in param_cols]) + f" {'PF':>8} {'vs_BASE':>8} {'Profit':>12} {'Sharpe':>8} {'DD%':>7} {'Trades':>7} {'Payoff':>9}")
print("-"*105)
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    params = " ".join([f"{str(row[p]):<22}" for p in param_cols])
    delta  = row["Profit Factor"] - baseline_pf
    flag   = " <-- GANA" if row["Profit Factor"] > baseline_pf else ""
    print(f"{rank:<4} {params} {row['Profit Factor']:>8.4f} {delta:>+8.4f} {row['Profit']:>12,.0f} {row['Sharpe Ratio']:>8.3f} {row['Equity DD %']:>7.2f}% {int(row['Trades']):>7} {row['Expected Payoff']:>9.2f}{flag}")
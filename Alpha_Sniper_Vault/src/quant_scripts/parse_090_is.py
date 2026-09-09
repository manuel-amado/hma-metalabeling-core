import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

# El archivo ya fue sobreescrito con la nueva optimizacion IS
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
param_cols = [c for c in df.columns if "Inp" in c]
num_cols   = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades","Expected Payoff","Recovery Factor"]
for c in num_cols + param_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Baseline IS puro (Reporte 101, IS 2022-2024)
baseline_pf_is     = 1.418
baseline_profit_is = 209637.0

df_sorted = df.sort_values("Profit Factor", ascending=False)

print(f"Total pases: {len(df)} | Parametros: {param_cols}")
print()
print(f"BASELINE IS (Master BASE 2022-2024): PF={baseline_pf_is} | Profit=${baseline_profit_is:,.0f}")
print()
header = f"{'#':<4} " + " ".join([f"{p:<24}" for p in param_cols]) + f" {'PF':>8} {'vs_IS':>8} {'Profit':>12} {'Sharpe':>8} {'DD%':>7} {'Trades':>7} {'Payoff':>9}"
print(header)
print("-" * len(header))
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    params = " ".join([f"{str(row[p]):<24}" for p in param_cols])
    delta  = row["Profit Factor"] - baseline_pf_is
    flag   = " <-- GANA IS" if delta > 0 else ""
    print(f"{rank:<4} {params} {row['Profit Factor']:>8.4f} {delta:>+8.4f} {row['Profit']:>12,.0f} {row['Sharpe Ratio']:>8.3f} {row['Equity DD %']:>7.2f}% {int(row['Trades']):>7} {row['Expected Payoff']:>9.2f}{flag}")
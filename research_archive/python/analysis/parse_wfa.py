import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

# 1. Cargar Reporte IS (XML anterior)
file_xml_is = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237091.xml"
with open(file_xml_is, "r", encoding="utf-8", errors="replace") as f:
    soup_is = BeautifulSoup(f.read(), "xml")
rows_is = soup_is.find_all("Row")
data_is, headers_is = [], []
for i, row in enumerate(rows_is):
    cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
    if i == 0: headers_is = cells
    elif len(cells) == len(headers_is): data_is.append(cells)
df_is = pd.DataFrame(data_is, columns=headers_is)

# 2. Cargar Reporte OOS / Forward (XML nuevo)
file_xml_oos = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237092.xml"
with open(file_xml_oos, "r", encoding="utf-8", errors="replace") as f:
    soup_oos = BeautifulSoup(f.read(), "xml")
rows_oos = soup_oos.find_all("Row")
data_oos, headers_oos = [], []
for i, row in enumerate(rows_oos):
    cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
    if i == 0: headers_oos = cells
    elif len(cells) == len(headers_oos): data_oos.append(cells)
df_oos = pd.DataFrame(data_oos, columns=headers_oos)

# Columnas paramétricas
param_cols = [c for c in df_is.columns if "Inp" in c]

# Conversión numérica IS
for c in ["Profit","Profit Factor","Equity DD %"] + param_cols:
    if c in df_is.columns: df_is[c] = pd.to_numeric(df_is[c], errors="coerce")

# Conversión numérica OOS
for c in ["Profit","Profit Factor","Equity DD %"] + param_cols:
    if c in df_oos.columns: df_oos[c] = pd.to_numeric(df_oos[c], errors="coerce")

# 3. Merge por parámetros para tener IS y OOS lado a lado
df_merged = pd.merge(df_is, df_oos, on=param_cols, suffixes=("_IS", "_OOS"))

# Baseline OOS (Reporte 101 OOS 25-26)
baseline_pf_oos = 1.502
baseline_dd_oos = 18.6 # Aprox %
baseline_pf_is  = 1.418

df_sorted = df_merged.sort_values("Profit Factor_IS", ascending=False)

print(f"Total pases coincidentes IS+OOS: {len(df_merged)}")
print()
print("="*115)
header = f"{'#':<3} " + " ".join([f"{p.replace('Inp',''):<18}" for p in param_cols]) + f" | {'PF IS':>6} {'PF OOS':>7} {'DeltaPF':>8} | {'DD% IS':>7} {'DD% OOS':>7}"
print(header)
print("="*115)

top_count = 0
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    params = " ".join([f"{str(int(row[p])):<18}" for p in param_cols])
    pf_is  = row["Profit Factor_IS"]
    pf_oos = row["Profit Factor_OOS"]
    delta  = pf_oos - pf_is
    dd_is  = row["Equity DD %_IS"]
    dd_oos = row["Equity DD %_OOS"]
    
    # Flags de validacion
    flag_pf = "✅" if pf_oos >= baseline_pf_oos else "❌"
    
    # Imprimir los top 15 y algunos representativos
    if rank <= 15 or rank % 10 == 0:
        print(f"{rank:<3} {params} | {pf_is:>6.3f} {pf_oos:>7.3f} {delta:>+8.3f} | {dd_is:>7.1f}% {dd_oos:>7.1f}%  {flag_pf}")
        top_count += 1
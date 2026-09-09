import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237098.html"

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

# La primera tabla suele tener el resumen
df_summary = tables[0]

profit = None
pf = None
trades = None

for i, row in df_summary.iterrows():
    for j, val in enumerate(row):
        if isinstance(val, str):
            val_lower = val.lower()
            if "beneficio neto total" in val_lower:
                profit = row[j+1]
            elif "factor de beneficio" in val_lower or "profit factor" in val_lower:
                pf = row[j+1]
            elif "transacciones totales" in val_lower or "total trades" in val_lower:
                trades = row[j+1]

print(f"--- RESULTADOS MASTER6 ONNX (ML FILTER) ---")
print(f"Beneficio Neto Total: {profit}")
print(f"Profit Factor: {pf}")
print(f"Transacciones Totales: {trades}")
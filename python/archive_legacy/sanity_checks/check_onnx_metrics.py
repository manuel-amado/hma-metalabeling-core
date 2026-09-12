import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237098.html"

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

df_summary = tables[0]
for i, row in df_summary.iterrows():
    # Only print rows that might contain the metrics we care about
    row_str = " | ".join([str(x) for x in row if pd.notna(x)])
    if any(kw in row_str.lower() for kw in ["beneficio", "transacciones", "factor", "total"]):
        print(row_str)
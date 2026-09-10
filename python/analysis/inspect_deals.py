import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237092.html"

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

df = tables[1]

# Display all rows where row contains "Transacciones" or check where the header of Transacciones is
for i, row in df.iterrows():
    if any(isinstance(x, str) and "Transacciones" in x for x in row):
        print(f"Row {i}: Transacciones header found")
        print(df.iloc[i+1])
        print(df.iloc[i+2])
        break
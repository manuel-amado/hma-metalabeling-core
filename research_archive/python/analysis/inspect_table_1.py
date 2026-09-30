import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237092.html"

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

df = tables[1]
print(df.head(10))
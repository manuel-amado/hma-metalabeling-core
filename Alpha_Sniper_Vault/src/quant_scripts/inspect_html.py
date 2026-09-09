import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237092.html"

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

# In MT5, the deals table is usually the last large table or has columns like "Direction"
deals_df = None
for idx, df in enumerate(tables):
    if len(df.columns) >= 10:
        # Convert first row to string to see if it matches
        header_row = df.iloc[0].astype(str).str.lower()
        if any("direction" in x or "dirección" in x for x in header_row) or any("out" in x or "in" in x for x in df.iloc[:, min(5, len(df.columns)-1)].astype(str).str.lower()):
            deals_df = df
            break

if deals_df is None:
    # Try just grabbing the largest table
    deals_df = max(tables, key=len)

print(deals_df.head(10))
print(f"\nShape: {deals_df.shape}")
import pandas as pd

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981370.html'
tables = pd.read_html(html_path)
deals_table = sorted(tables, key=lambda t: len(t))[-1]

print("Columns:", list(deals_table.columns))
print("\nFirst 3 rows:")
print(deals_table.head(3).to_string())
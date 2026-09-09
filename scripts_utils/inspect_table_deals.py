import pandas as pd

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981370.html'
tables = pd.read_html(html_path)
deals_table = sorted(tables, key=lambda t: len(t))[-1]

# Find where Transacciones starts
start_idx = -1
for idx, row in deals_table.iterrows():
    if 'Transacciones' in str(row.values):
        start_idx = idx
        break

print(f'Transacciones starts at row {start_idx}')
if start_idx != -1:
    print(deals_table.iloc[start_idx:start_idx+5].to_string())
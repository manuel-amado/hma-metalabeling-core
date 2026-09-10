from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237085.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    soup = BeautifulSoup(f, 'xml')

rows = soup.find_all('Row')

data = []
for row in rows:
    cells = row.find_all('Cell')
    row_data = []
    for cell in cells:
        data_tag = cell.find('Data')
        if data_tag:
            row_data.append(data_tag.text)
        else:
            row_data.append("")
    if row_data:
        data.append(row_data)

if data:
    # First row is usually headers
    headers = data[0]
    print(headers)
    
    # Let's print first 3 data rows
    for r in data[1:4]:
        print(r)
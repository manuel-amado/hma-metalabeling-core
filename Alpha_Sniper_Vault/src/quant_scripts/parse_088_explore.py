from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237088.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

soup = BeautifulSoup(content, 'xml')
rows = soup.find_all('Row')

data = []
headers = []
for i, row in enumerate(rows):
    cells = row.find_all('Cell')
    row_data = [cell.get_text(strip=True) for cell in cells]
    if i == 0:
        headers = row_data
    else:
        if len(row_data) == len(headers):
            data.append(row_data)

df = pd.DataFrame(data, columns=headers)
print(f"Columnas: {list(df.columns)}")
print(f"Total pases: {len(df)}")
print(df.head(3).to_string())
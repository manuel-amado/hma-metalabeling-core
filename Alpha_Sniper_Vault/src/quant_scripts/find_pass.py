import pandas as pd
from bs4 import BeautifulSoup

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237094.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    soup = BeautifulSoup(f, 'xml')

rows = soup.find_all('Row')
data = []
for row in rows:
    cells = row.find_all('Cell')
    row_data = [cell.find('Data').text if cell.find('Data') else "" for cell in cells]
    if row_data:
        data.append(row_data)

if data:
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)
    
    # Convert inputs to float
    for col in ['InpATRMultiplier', 'InpRSILongOrigin', 'InpRSIShortOrigin', 'InpMaxImpulseATR']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Find the specific row
    target_row = df[(df['InpATRMultiplier'] == 1.4) & 
                    (df['InpRSILongOrigin'] == 48) & 
                    (df['InpRSIShortOrigin'] == 60) & 
                    (df['InpMaxImpulseATR'] == 4.0)]
                    
    print(target_row[['Pass', 'Profit Factor', 'Profit', 'Trades', 'Equity DD %']].to_string(index=False))
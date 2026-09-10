from bs4 import BeautifulSoup
import pandas as pd

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
    
    numeric_cols = ['Profit Factor', 'Profit', 'Equity DD %', 'Trades']
    exp_cols = [c for c in headers if c.startswith('InpATRMultiplier') or c.startswith('InpRSILongOrigin') or c.startswith('InpRSIShortOrigin') or c.startswith('InpMaxImpulseATR')]
    numeric_cols.extend(exp_cols)
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df = df.dropna(subset=['Profit Factor'])
    
    print("=== AUDITORIA LINEAL (SIN INTERES COMPUESTO) ===")
    
    for exp_col in exp_cols:
        print(f"\nImpacto de: {exp_col}")
        grp = df.groupby(exp_col).agg(
            Count=('Profit Factor', 'count'),
            Median_PF=('Profit Factor', 'median'),
            Mean_Profit=('Profit', 'mean'),
            Mean_DD=('Equity DD %', 'mean'),
            Mean_Trades=('Trades', 'mean')
        ).round(2)
        print(grp.to_string())
        
    print("\nTop 5 Mejores Configuraciones Absolutas por Profit Factor:")
    top_5 = df.sort_values(by='Profit Factor', ascending=False).head(5)
    cols_to_print = exp_cols + ['Profit Factor', 'Profit', 'Equity DD %', 'Trades']
    print(top_5[cols_to_print].to_string(index=False))
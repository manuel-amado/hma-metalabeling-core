from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237087.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

soup = BeautifulSoup(content, 'xml')

# Buscar todas las filas (Row)
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
        elif len(row_data) > 0:
            # A veces hay filas incompletas
            pass

if len(data) > 0 and len(headers) > 0:
    df = pd.DataFrame(data, columns=headers)
    
    # Clean numeric columns
    numeric_cols = ['Result', 'Profit', 'Trades', 'Profit Factor', 'Expected Payoff', 'Drawdown %']
    for col in df.columns:
        if col in numeric_cols or 'Inp' in col or 'Trigger' in col or 'Partial' in col or 'Trail' in col:
            try:
                df[col] = pd.to_numeric(df[col].str.replace(' ', '').str.replace(',', '.'))
            except:
                pass
                
    # Mostrar el Top 10 por Profit Factor (con mas de 100 trades para filtrar ruido)
    if 'Trades' in df.columns:
        df['Trades'] = pd.to_numeric(df['Trades'])
        df_valid = df[df['Trades'] > 100].copy()
    else:
        df_valid = df.copy()
        
    if 'Profit Factor' in df_valid.columns:
        df_valid['Profit Factor'] = pd.to_numeric(df_valid['Profit Factor'])
        df_sorted = df_valid.sort_values('Profit Factor', ascending=False)
        print("--- TOP 10 POR PROFIT FACTOR ---")
        cols_to_show = ['Pass', 'Profit', 'Trades', 'Profit Factor'] + [c for c in df_valid.columns if 'Inp' in c or 'R-' in c or 'Dist' in c]
        print(df_sorted[cols_to_show].head(10).to_string(index=False))
        
    print("\n--- TOP 10 POR PROFIT (NETO) ---")
    if 'Profit' in df_valid.columns:
        df_valid['Profit'] = pd.to_numeric(df_valid['Profit'])
        df_sorted_profit = df_valid.sort_values('Profit', ascending=False)
        print(df_sorted_profit[cols_to_show].head(10).to_string(index=False))
else:
    print("No se pudo parsear el XML correctamente.")
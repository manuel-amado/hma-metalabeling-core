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
    numeric_cols = ['Profit Factor', 'Profit', 'Equity DD %', 'Trades', 'InpATRMultiplier', 'InpRSILongOrigin', 'InpRSIShortOrigin', 'InpMaxImpulseATR']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['Profit Factor'])

    print("=== ANALISIS MULTIDIMENSIONAL ===")
    
    # Let's group by ImpulseATR and ATRMultiplier
    print("\n1. Interaccion: MaxImpulseATR vs ATRMultiplier (Top 10)")
    grp1 = df.groupby(['InpMaxImpulseATR', 'InpATRMultiplier']).agg(
        Median_PF=('Profit Factor', 'median'),
        Mean_Profit=('Profit', 'mean'),
        Mean_DD=('Equity DD %', 'mean')
    ).reset_index().sort_values(by='Median_PF', ascending=False).head(10)
    print(grp1.to_string(index=False))

    # Let's filter df to only the "Good" RSI parameters to see true performance
    good_rsi_df = df[(df['InpRSILongOrigin'] >= 46) & (df['InpRSILongOrigin'] <= 48) & (df['InpRSIShortOrigin'] == 60)]
    
    print("\n2. Rendimiento de ImpulseATR cuando RSI es optimo (Long 46-48, Short 60):")
    grp2 = good_rsi_df.groupby('InpMaxImpulseATR').agg(
        Count=('Profit Factor', 'count'),
        Median_PF=('Profit Factor', 'median'),
        Mean_Profit=('Profit', 'mean'),
        Mean_DD=('Equity DD %', 'mean'),
        Mean_Trades=('Trades', 'mean')
    ).round(2).reset_index().sort_values(by='Median_PF', ascending=False)
    print(grp2.to_string(index=False))

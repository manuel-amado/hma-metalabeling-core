from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

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
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)
    
    # Convert numeric columns
    numeric_cols = ['Profit', 'Profit Factor', 'Equity DD %', 'Trades', 'InpATRMultiplier', 'InpRSILongOrigin', 'InpRSIShortOrigin']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=['Profit Factor', 'InpATRMultiplier'])
    
    print("=== AUDITORIA DE OPTIMIZACION: BUSCANDO MESETAS ROBUSTAS ===")
    
    print("\n1. Impacto del ATR Multiplier (El Peaje)")
    atr_group = df.groupby('InpATRMultiplier').agg(
        Count=('Profit Factor', 'count'),
        Median_PF=('Profit Factor', 'median'),
        Mean_PF=('Profit Factor', 'mean'),
        Mean_Profit=('Profit', 'mean'),
        Mean_DD=('Equity DD %', 'mean'),
        Mean_Trades=('Trades', 'mean')
    ).round(2)
    print(atr_group.to_string())
    
    print("\n2. Impacto de InpRSILongOrigin (Confirmación del Retroceso Alcista)")
    long_origin_group = df.groupby('InpRSILongOrigin').agg(
        Count=('Profit Factor', 'count'),
        Median_PF=('Profit Factor', 'median'),
        Mean_Profit=('Profit', 'mean'),
        Mean_DD=('Equity DD %', 'mean')
    ).round(2)
    print(long_origin_group.to_string())
    
    print("\n3. Impacto de InpRSIShortOrigin (Confirmación del Retroceso Bajista)")
    short_origin_group = df.groupby('InpRSIShortOrigin').agg(
        Count=('Profit Factor', 'count'),
        Median_PF=('Profit Factor', 'median'),
        Mean_Profit=('Profit', 'mean'),
        Mean_DD=('Equity DD %', 'mean')
    ).round(2)
    print(short_origin_group.to_string())
    
    # Get the Top 10 configurations based on Profit Factor
    print("\n4. Top 5 Configuraciones Absolutas por Profit Factor")
    top_5 = df.sort_values(by='Profit Factor', ascending=False).head(5)
    print(top_5[['InpATRMultiplier', 'InpRSILongOrigin', 'InpRSIShortOrigin', 'Profit Factor', 'Profit', 'Equity DD %', 'Trades']].to_string(index=False))

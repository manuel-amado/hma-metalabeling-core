import pandas as pd
import numpy as np

html_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\HarvestReport.htm'
try:
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    trades = []
    # Split by rows
    rows = content.split('<tr')
    for row in rows:
        if 'class="msdate"' in row and ('buy' in row or 'sell' in row):
            # Try to extract the date
            # Usually <td class="msdate">2019.04.05 18:00</td>
            try:
                date_part = row.split('class="msdate">')[1].split('</td>')[0]
                year = int(date_part.split('.')[0])
                
                if '>buy<' in row:
                    trades.append({'Year': year, 'Type': 'buy'})
                elif '>sell<' in row:
                    trades.append({'Year': year, 'Type': 'sell'})
            except:
                pass
                
    if len(trades) == 0:
        print("No se encontraron operaciones en el HTML usando parseo manual.")
    else:
        df_trades = pd.DataFrame(trades)
        df_trades['Dataset'] = np.where(df_trades['Year'] >= 2023, 'OOS (Out-of-Sample)', 'IS (Entrenamiento)')
        
        metrics = df_trades.groupby(['Year', 'Dataset']).agg(
            Num_Operaciones=('Year', 'count')
        ).reset_index()
        
        print('--- NUMERO DE OPERACIONES POR AÑO ---')
        print(metrics.to_string(index=False))
        
        csv_path = r'c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sweep_Dataset_XAUUSD.csv'
        df_csv = pd.read_csv(csv_path)
        
        if len(df_csv) == len(df_trades):
            df_csv['Year'] = df_trades['Year']
            df_csv['Dataset'] = df_trades['Dataset']
            
            detailed_metrics = df_csv.groupby(['Year', 'Dataset']).agg(
                Num_Operaciones=('Label', 'count'),
                Win_Rate=('Label', lambda x: (x == 1).mean() * 100),
                Net_R=('ReturnPct', 'sum'),
                Avg_R=('ReturnPct', 'mean')
            ).reset_index()
            
            detailed_metrics['Win_Rate'] = detailed_metrics['Win_Rate'].round(2).astype(str) + '%'
            detailed_metrics['Net_R'] = detailed_metrics['Net_R'].round(2)
            detailed_metrics['Avg_R'] = detailed_metrics['Avg_R'].round(2)
            
            print('\n--- METRICAS DETALLADAS AÑO POR AÑO (Desde CSV + HTML) ---')
            print(detailed_metrics.to_string(index=False))
            
            print('\n--- METRICAS GLOBALES IS vs OOS ---')
            global_metrics = df_csv.groupby('Dataset').agg(
                Num_Operaciones=('Label', 'count'),
                Win_Rate=('Label', lambda x: (x == 1).mean() * 100),
                Net_R=('ReturnPct', 'sum'),
                Avg_R=('ReturnPct', 'mean')
            ).reset_index()
            global_metrics['Win_Rate'] = global_metrics['Win_Rate'].round(2).astype(str) + '%'
            global_metrics['Net_R'] = global_metrics['Net_R'].round(2)
            global_metrics['Avg_R'] = global_metrics['Avg_R'].round(2)
            print(global_metrics.to_string(index=False))
        else:
            print(f"\nDesajuste de filas: CSV={len(df_csv)}, HTML={len(df_trades)}. No se pueden fusionar las métricas de NetR.")
except Exception as e:
    print('Error:', e)

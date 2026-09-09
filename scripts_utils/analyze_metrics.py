import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('c:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sweep_Dataset_XAUUSD.csv')

# Ensure datetime is parsed
df['EntryTime'] = pd.to_datetime(df['EntryTime'])
df['Year'] = df['EntryTime'].dt.year

# Define OOS threshold (typically 2023-01-01 for this project, let's use year >= 2023 as OOS)
df['Dataset'] = np.where(df['Year'] >= 2023, 'OOS (Out-of-Sample)', 'IS (Entrenamiento)')

# Group by Year and Dataset
metrics = df.groupby(['Year', 'Dataset']).agg(
    Num_Operaciones=('Label', 'count'),
    Win_Rate=('Label', lambda x: (x == 1).mean() * 100),
    Net_R=('NetR', 'sum'),
    Avg_R=('NetR', 'mean')
).reset_index()

# Format floats
metrics['Win_Rate'] = metrics['Win_Rate'].round(2).astype(str) + '%'
metrics['Net_R'] = metrics['Net_R'].round(2)
metrics['Avg_R'] = metrics['Avg_R'].round(2)

print('--- METRICAS AÑO POR AÑO ---')
print(metrics.to_string(index=False))

print('\n--- METRICAS GLOBALES IS vs OOS ---')
global_metrics = df.groupby('Dataset').agg(
    Num_Operaciones=('Label', 'count'),
    Win_Rate=('Label', lambda x: (x == 1).mean() * 100),
    Net_R=('NetR', 'sum'),
    Avg_R=('NetR', 'mean')
).reset_index()

global_metrics['Win_Rate'] = global_metrics['Win_Rate'].round(2).astype(str) + '%'
global_metrics['Net_R'] = global_metrics['Net_R'].round(2)
global_metrics['Avg_R'] = global_metrics['Avg_R'].round(2)
print(global_metrics.to_string(index=False))


import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data\Alpha_Sweep_Dataset_v20_XAUUSD.csv')
df['Time'] = pd.to_datetime(df['Time'], format='mixed')
df = df.dropna().sort_values('Time').reset_index(drop=True)

df_2022_2025 = df[(df['Time'].dt.year >= 2022) & (df['Time'].dt.year <= 2025)]
print(f"Total crosses extracted in 2022-2025: {len(df_2022_2025)}")

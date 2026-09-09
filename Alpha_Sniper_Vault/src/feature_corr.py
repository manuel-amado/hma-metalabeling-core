import pandas as pd
import numpy as np

# Load XAUUSD dataset to compute correlations
df = pd.read_csv(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data\Alpha_Sweep_Dataset_v16_1_XAUUSD.csv')
features = ['SignalType', 'RSIExt', 'DistAsianLow', 'HMAAccelF', 'DistAsianHigh', 'RSI', 'BarsVolShock', 'DistRunwayHMA200', 'RSI_Memory_State']

print("=== CORRELACIONES LINEALES CON EL EXITO (Label) EN XAUUSD ===")
for f in features:
    if f in df.columns:
        corr = df[f].corr(df['Label'])
        print(f"{f}: {corr:.4f}")
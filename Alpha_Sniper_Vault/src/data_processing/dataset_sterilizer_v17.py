import pandas as pd
import numpy as np
import os

print("=== ALPHA SNIPER V17: DATASET STERILIZER ===")

# Rutas
DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
CALENDAR_PATH = r'C:\Users\Manuel\Downloads\calendar-event-list (1).csv'

# 1. Cargar Calendario
print("Cargando calendario economico...")
cal_df = pd.read_csv(CALENDAR_PATH)
cal_df['Start'] = pd.to_datetime(cal_df['Start'], format='%m/%d/%Y %H:%M:%S', errors='coerce')
cal_df = cal_df.dropna(subset=['Start'])

# Lista de palabras clave para filtrar noticias que realmente destruyen la estructura tecnica
toxic_keywords = ['Nóminas no agrícolas', 'Índice de Precios al Consumo', 'Decisión sobre la tasa de interés', 
                  'Decisión de tipos de interés', 'Declaración de política monetaria', 'Minutas del FOMC', 
                  'Conferencia de prensa del FOMC', 'Conferencia de prensa del BoJ']

cal_filtered = cal_df[cal_df['Name'].str.contains('|'.join(toxic_keywords), case=False, na=False)].copy()
print(f"Noticias macroeconomicas filtradas (Toxicas): {len(cal_filtered)} eventos.")

# Set up sets for fast lookup if needed, but iterating is fine for <5000 rows
def is_blacklisted(ts, symbol):
    if ts.hour == 23 or ts.hour == 0:
        return True, "Rollover"
    
    if (ts.month == 12 and ts.day >= 24) or (ts.month == 1 and ts.day <= 2):
        return True, "Festividad"
    
    currency_to_check = 'USD'
    if 'JPY' in symbol: currency_to_check = 'JPY'
    elif 'EUR' in symbol: currency_to_check = 'EUR'
    
    if 'USD' in symbol or 'XAU' in symbol:
        events = cal_filtered[cal_filtered['Currency'] == 'USD']
    else:
        events = cal_filtered[cal_filtered['Currency'] == currency_to_check]
    
    # Delta hours
    deltas = (ts - events['Start']).dt.total_seconds() / 3600.0
    if ((deltas >= -2.0) & (deltas <= 4.0)).any():
        return True, "Noticia Macro"
            
    return False, ""

# 2. Procesar cada CSV de V17
symbols = ['XAUUSD', 'EURUSD', 'USDJPY']
for sym in symbols:
    csv_path = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_{sym}.csv')
    if not os.path.exists(csv_path):
        print(f"Esperando a que extraigas el CSV de V17 para {sym} (Aun no existe).")
        continue
        
    print(f"\nProcesando {sym}...")
    df = pd.read_csv(csv_path)
    if 'Time' not in df.columns:
        print(f"ERROR: {sym} no tiene la columna 'Time'.")
        continue
        
    df['Time'] = pd.to_datetime(df['Time'])
    
    drop_indices = []
    reasons = {'Rollover': 0, 'Festividad': 0, 'Noticia Macro': 0}
    
    for idx, row in df.iterrows():
        blacklisted, reason = is_blacklisted(row['Time'], sym)
        if blacklisted:
            drop_indices.append(idx)
            reasons[reason] += 1
            
    df_clean = df.drop(index=drop_indices)
    
    print(f"Senales Originales: {len(df)}")
    print(f"Senales Purgadas: {len(drop_indices)}")
    for r, count in reasons.items():
        if count > 0: print(f"  - Por {r}: {count}")
    print(f"Senales Limpias: {len(df_clean)}")
    
    out_path = os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v17_STERILIZED_{sym}.csv')
    df_clean.to_csv(out_path, index=False)
    print(f"Dataset esterilizado guardado en: {out_path}")

print("\nFinalizado.")
import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Revert Entry truncation
target_entry = '''    # Fase 41: Regime Truncation (Nuevo Paradigma)
    df = df[df["Time"] >= "2023-01-01"].copy()
    print(f"  [REGIME TRUNCATION] Filas Post-2023: {len(df):,}")

    df = df.sort_values("Time").reset_index(drop=True)'''

replacement_entry = '''    df = df.sort_values("Time").reset_index(drop=True)'''
content = content.replace(target_entry, replacement_entry)

# Revert Exit truncation
target_exit = '''    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        df = df[df["Time"] >= "2023-01-01"].copy()
        print(f"  [REGIME TRUNCATION] Dilemmas Post-2023: {len(df):,}")
        
    print(f"  Filas totales (exit dilemmas): {len(df):,}")'''

replacement_exit = '''    print(f"  Filas totales (exit dilemmas): {len(df):,}")'''
content = content.replace(target_exit, replacement_exit)

# Revert WFO start_date
target_wfo = "start_date = df_clean['Time'].min() + pd.DateOffset(years=1) # Reduced to 1 year for Phase 41"
replacement_wfo = "start_date = df_clean['Time'].min()" # actually start_date is min_date, let's just make it min_date
content = content.replace(target_wfo, "start_date = df_clean['Time'].min()")

# Revert WFO current_end
target_wfo2 = "current_end = start_date + pd.DateOffset(months=12) # Reduced to 1 year for Phase 41"
replacement_wfo2 = "current_end = start_date + pd.DateOffset(months=60) # 5 years min history"
content = content.replace(target_wfo2, replacement_wfo2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Reverted dataset truncation and WFO window')

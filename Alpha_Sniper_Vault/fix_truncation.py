import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Entry
target_entry = '''    # Convertir Time a datetime y ordenar cronologicamente (Zero Look-Ahead)
    df["Time"] = pd.to_datetime(df["Time"])

    df = df.sort_values("Time").reset_index(drop=True)'''

replacement_entry = '''    # Convertir Time a datetime y ordenar cronologicamente (Zero Look-Ahead)
    df["Time"] = pd.to_datetime(df["Time"])
    
    # Fase 41: Regime Truncation (Nuevo Paradigma)
    df = df[df["Time"] >= "2023-01-01"].copy()
    print(f"  [REGIME TRUNCATION] Filas Post-2023: {len(df):,}")

    df = df.sort_values("Time").reset_index(drop=True)'''

# Exit
target_exit = '''def cargar_exit_dataset(exit_csv: str) -> tuple:
    print(f"\n[EXIT DATA] Cargando: {exit_csv}")
    df = pd.read_csv(exit_csv)
    print(f"  Filas totales (exit dilemmas): {len(df):,}")'''

replacement_exit = '''def cargar_exit_dataset(exit_csv: str) -> tuple:
    print(f"\n[EXIT DATA] Cargando: {exit_csv}")
    df = pd.read_csv(exit_csv)
    
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        df = df[df["Time"] >= "2023-01-01"].copy()
        print(f"  [REGIME TRUNCATION] Dilemmas Post-2023: {len(df):,}")
        
    print(f"  Filas totales (exit dilemmas): {len(df):,}")'''

content = content.replace(target_entry, replacement_entry)
content = content.replace(target_exit, replacement_exit)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Pipeline updated with Regime Truncation')

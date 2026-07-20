import os
import glob
import pandas as pd

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Python_ML\data"

def sanitize_csv(filepath):
    # Intentar leer con tabulaciones o comas si es necesario, pero usualmente es coma.
    try:
        df = pd.read_csv(filepath, low_memory=False)
        if df.shape[1] == 1:
            df = pd.read_csv(filepath, sep="\t", low_memory=False)
    except Exception as e:
        print(f"[ERROR] No se pudo leer {os.path.basename(filepath)}: {e}")
        return 0
        
    df.columns = df.columns.str.strip()
    
    if 'Time' not in df.columns:
        print(f"[WARN] No se encontró columna 'Time' en {os.path.basename(filepath)}. Omitiendo.")
        return 0

    original_len = len(df)
    
    # Asegurar orden cronológico primero
    df['Time_DT'] = pd.to_datetime(df['Time'])
    df = df.sort_values(by='Time_DT')
    
    # Deduplicar basado en Time (manteniendo la primera ocurrencia)
    df = df.drop_duplicates(subset=['Time'], keep='first')
    
    df = df.drop(columns=['Time_DT'])
    
    final_len = len(df)
    removed = original_len - final_len
    
    # Sobreescribir archivo si hubo cambios o solo por seguridad de orden
    df.to_csv(filepath, index=False)
    
    return removed

def main():
    print("="*60)
    print(" FORENSIC DATA SANITIZATION (DEDUPLICATION & SORTING)")
    print("="*60)
    
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    total_removed = 0
    results = {}
    
    for f in csv_files:
        filename = os.path.basename(f)
        removed = sanitize_csv(f)
        results[filename] = removed
        total_removed += removed
        
    # Agrupar por activo para el reporte de daños
    activos = set()
    for fname in results.keys():
        if "Struct_Dataset_" in fname:
            sym = fname.replace("Struct_Dataset_", "").replace(".csv", "")
            activos.add(sym)
            
    print("\n[REPORTE DE DAÑOS]")
    print(f"Total de filas duplicadas extirpadas globalmente: {total_removed}")
    print("-" * 40)
    
    for sym in sorted(activos):
        entry_file = f"Struct_Dataset_{sym}.csv"
        exit_file = f"Struct_Exit_Dataset_{sym}.csv"
        
        r_entry = results.get(entry_file, 0)
        r_exit = results.get(exit_file, 0)
        
        if r_entry > 0 or r_exit > 0:
            print(f"  > {sym.upper()}: {r_entry} duplicados en Entry, {r_exit} duplicados en Exit")
        else:
            print(f"  > {sym.upper()}: 0 duplicados (Limpio)")

    print("\nSanitización completada. Los datasets están cronológicamente ordenados y libres de toxicidad por duplicación.")

if __name__ == "__main__":
    main()

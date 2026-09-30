import os
import glob
import pandas as pd
import shutil

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
BACKUP_DIR = os.path.join(DATA_DIR, "backup_full_v16")

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Target all v16 CSVs that don't have "2026" or "Train" in the name to avoid double processing
    all_files = glob.glob(os.path.join(DATA_DIR, "Alpha_Sweep_Dataset_v16*.csv"))
    valid_files = [f for f in all_files if "_2026.csv" not in f and "backup" not in f]
    
    # 5.5% represents approximately the year 2026 out of the 11.6 years (2015-2026.08) dataset
    OOS_RATIO = 0.055 
    
    for file_path in valid_files:
        filename = os.path.basename(file_path)
        
        # 1. Backup original file
        backup_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            shutil.copy2(file_path, backup_path)
            print(f"Copia de seguridad creada: {backup_path}")
            
        # 2. Read dataset
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # 3. Calculate split index
        split_idx = int(total_rows * (1 - OOS_RATIO))
        
        # 4. Split data
        df_train = df.iloc[:split_idx].copy()
        df_oos_2026 = df.iloc[split_idx:].copy()
        
        # 5. Save Train Data (Overwrite original)
        df_train.to_csv(file_path, index=False)
        
        # 6. Save OOS 2026 Data
        oos_filename = filename.replace(".csv", "_2026.csv")
        oos_path = os.path.join(DATA_DIR, oos_filename)
        df_oos_2026.to_csv(oos_path, index=False)
        
        print(f"[{filename}] Original: {total_rows} filas | Train (Pre-2026): {len(df_train)} | OOS (2026): {len(df_oos_2026)}")

if __name__ == "__main__":
    main()

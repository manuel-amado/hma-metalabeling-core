import os
import time
import shutil
import subprocess
import pandas as pd

def main():
    print("[MONITOR] Iniciando monitorización robusta (Detección de Bloqueo de Archivos)...")
    
    source_dir = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
    dest_dir = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data"
    project_dir = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault"
    
    # Guardar mtimes conocidos para detectar cambios
    last_mtimes = {}
    
    while True:
        locked_files = False
        newly_copied = []
        
        now = time.time()
        
        for f in os.listdir(source_dir):
            if f.endswith(".csv"):
                src_path = os.path.join(source_dir, f)
                current_mtime = os.path.getmtime(src_path)
                
                # Si el archivo fue modificado en las ultimas 24h y es más nuevo de lo que conociamos
                if (now - current_mtime) < 86400 and current_mtime > last_mtimes.get(f, 0):
                    try:
                        shutil.copy2(src_path, os.path.join(dest_dir, f))
                        last_mtimes[f] = current_mtime
                        newly_copied.append(f)
                        print(f"[MONITOR] Archivo liberado y copiado: {f}")
                    except PermissionError:
                        # El archivo esta bloqueado por MT5, el backtest sigue corriendo
                        locked_files = True
        
        if locked_files:
            print("[MONITOR] MetaTrader sigue escribiendo datos... Esperando 60 segundos.")
            time.sleep(60)
            continue
            
        # Si llegamos aqui, ningun archivo esta bloqueado.
        if len(newly_copied) > 0:
            print("[MONITOR] Todos los bloqueos han sido liberados. Procesando archivos nuevos...")
            updated_symbols = []
            
            for f in newly_copied:
                if f.startswith("Struct_Dataset_"):
                    sym = f.replace("Struct_Dataset_", "").replace(".csv", "")
                    try:
                        df_head = pd.read_csv(os.path.join(dest_dir, f), nrows=1)
                        if "MAE_ATR" in df_head.columns:
                            updated_symbols.append(sym)
                    except Exception as e:
                        print(f"[MONITOR] Error verificando cabeceras de {f}: {e}")
                        
            updated_symbols = list(set(updated_symbols))
            if len(updated_symbols) > 0:
                symbols_str = ",".join(updated_symbols)
                print(f"[MONITOR] Lanzando pipeline global para: {symbols_str}")
                cmd_pipeline = f".venv\\Scripts\\python.exe src\\pipeline_global_optimizer.py --symbols {symbols_str}"
                subprocess.run(cmd_pipeline, cwd=project_dir, shell=True)
                print("[MONITOR] Pipeline completado. Volviendo a patrullar...")
            else:
                print("[MONITOR] Archivos copiados pero ninguno contenía la marca MAE_ATR.")
                
        time.sleep(60)

if __name__ == '__main__':
    main()

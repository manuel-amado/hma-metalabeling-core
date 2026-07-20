import os
import subprocess
import sys

def main():
    # The Master 8 (Canasta Optimizada)
    activos = [
        "USDJPY", "GBPUSD", "EURUSD", "EURJPY", 
        "XAUUSD", "XAGUSD", "US30.cash", "US500.cash"
    ]
    
    script_path = "pipeline_global_optimizer.py"
    
    if not os.path.exists(script_path):
        print(f"ERROR: No se encontró {script_path}")
        return
        
    for activo in activos:
        print("\n" + "="*80)
        print(f" INICIANDO ENTRENAMIENTO PARA: {activo}")
        print("="*80)
        
        # Ejecutar el proceso secuencialmente (Multithreading se maneja internamente por XGBoost)
        try:
            result = subprocess.run(
                [sys.executable, script_path, activo],
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] El entrenamiento falló para {activo}. Error Code: {e.returncode}")
        except Exception as e:
            print(f"[ERROR] Error inesperado con {activo}: {e}")

if __name__ == "__main__":
    main()

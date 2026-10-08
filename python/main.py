import os
import sys
import time
import subprocess
from pathlib import Path

# Definir la raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent
PYTHON_DIR = ROOT_DIR / "python" / "m2_metalabeling"

def print_header():
    print("=" * 60)
    print("    M2 QUANT PIPELINE - INSTITUTIONAL CONTROL PANEL     ")
    print("=" * 60)
    print(" Basado en Marcos López de Prado (Advances in Financial ML)")
    print(" Framework de latencia cero para MetaTrader 5")
    print("=" * 60)

def print_menu():
    print("\n[ FLUJO DE EJECUCIÓN (WORKFLOW) ]")
    print("  1. Ingestar Datos y Aplicar Triple-Barrera (Meta-Labeling)")
    print("  2. Entrenar Modelos (Purged Walk-Forward Montecarlo)")
    print("  3. Auditoría Estricta contra Fuga de Datos (Sanity Check)")
    print("  4. Transpilar Oráculo a C++ (MQL5 0ms Latency)")
    print("  5. Ejecutar Flujo Completo (Portfolio Auto-Batch)")
    print("\n[ OPCIONES ]")
    print("  0. Salir")
    print("-" * 60)

def run_script(script_path: Path):
    if not script_path.exists():
        print(f"❌ Error: No se encontró el módulo en {script_path}")
        return
    
    print(f"\n🚀 Ejecutando: {script_path.name}...")
    try:
        # Ejecutar en un subproceso para mantener el aislamiento del entorno
        subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"✅ Finalizado con éxito: {script_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la ejecución de {script_path.name}. Código: {e.returncode}")
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header()
        print_menu()
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n>> Iniciando Ingesta y Etiquetado Triple-Barrera...")
            run_script(PYTHON_DIR / "ingestion" / "mt5_reader.py")
            run_script(PYTHON_DIR / "labeling" / "triple_barrier.py")
            time.sleep(2)
        elif opcion == "2":
            print("\n>> Entrenando Modelos en Ventanas Rodantes (Purged WFM)...")
            run_script(PYTHON_DIR / "models" / "rolling_window_retrain.py")
            time.sleep(2)
        elif opcion == "3":
            print("\n>> Ejecutando Auditoría Institucional de Fuga de Datos...")
            run_script(PYTHON_DIR / "models" / "audit_report.py")
            input("\nPresiona Enter para volver al menú...")
        elif opcion == "4":
            print("\n>> Transpilando Árboles de Decisión a C++ (.mqh)...")
            run_script(PYTHON_DIR / "models" / "export_factory_oracle.py")
            time.sleep(2)
        elif opcion == "5":
            print("\n>> Ejecutando Pipeline Institucional Completo...")
            run_script(PYTHON_DIR / "models" / "portfolio_factory.py")
            print("\n🎉 Flujo completo finalizado.")
            input("\nPresiona Enter para volver al menú...")
        elif opcion == "0":
            print("\nCerrando Panel de Control M2. ¡Buen trading institucional!\n")
            break
        else:
            print("\n❌ Opción no válida.")
            time.sleep(1)

if __name__ == "__main__":
    main()

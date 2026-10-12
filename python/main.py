"""
M2 Meta-Labeling Pipeline — Main CLI Orchestrator
===================================================
Institutional Control Panel and Headless Automation Runner.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Safe stdout reconfiguration for Windows environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Resolve project root dynamically
ROOT_DIR = Path(__file__).resolve().parent.parent
PYTHON_DIR = ROOT_DIR / "python" / "m2_metalabeling"


def print_header():
    print("=" * 60)
    print("    M2 QUANT PIPELINE - INSTITUTIONAL CONTROL PANEL     ")
    print("=" * 60)
    print(" Basado en Marcos Lopez de Prado (Advances in Financial ML)")
    print(" Framework de latencia cero para MetaTrader 5")
    print("=" * 60)


def print_menu():
    print("\n[ FLUJO DE EJECUCION (WORKFLOW) ]")
    print("  1. Ingestar Datos y Aplicar Triple-Barrera (Meta-Labeling)")
    print("  2. Entrenar Modelos (Purged Walk-Forward Montecarlo)")
    print("  3. Auditoria Estricta contra Fuga de Datos (Sanity Check)")
    print("  4. Transpilar Oraculo a C++ (MQL5 0ms Latency)")
    print("  5. Ejecutar Flujo Completo (Portfolio Auto-Batch)")
    print("\n[ OPCIONES ]")
    print("  0. Salir")
    print("-" * 60)


def run_script(script_path: Path) -> bool:
    """Execute a python script as a subprocess with proper PYTHONPATH."""
    if not script_path.exists():
        print(f"[-] Error: No se encontro el modulo en {script_path}")
        return False

    print(f"\n[*] Ejecutando: {script_path.name}...")
    env = os.environ.copy()
    python_dir_str = str(ROOT_DIR / "python")
    env["PYTHONPATH"] = (
        f"{python_dir_str};{env.get('PYTHONPATH', '')}"
        if os.name == "nt"
        else f"{python_dir_str}:{env.get('PYTHONPATH', '')}"
    )
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        subprocess.run([sys.executable, str(script_path)], env=env, check=True)
        print(f"[OK] Finalizado con exito: {script_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Error en la ejecucion de {script_path.name}. Codigo: {e.returncode}")
        return False
    except Exception as e:
        print(f"[-] Error critico: {str(e)}")
        return False


def execute_step(step: str) -> bool:
    """Execute a specific pipeline step or all steps."""
    step = str(step).lower()
    success = True

    if step in ("1", "all"):
        print("\n>> Iniciando Ingesta y Etiquetado Triple-Barrera...")
        s1 = run_script(PYTHON_DIR / "ingestion" / "mt5_reader.py")
        s2 = run_script(PYTHON_DIR / "labeling" / "triple_barrier.py")
        success = success and s1 and s2

    if step in ("2", "all"):
        print("\n>> Entrenando Modelos en Ventanas Rodantes (Purged WFM)...")
        s = run_script(PYTHON_DIR / "models" / "rolling_window_retrain.py")
        success = success and s

    if step in ("3", "all"):
        print("\n>> Ejecutando Auditoria Institucional de Fuga de Datos...")
        s1 = run_script(PYTHON_DIR / "models" / "audit_report.py")
        s2 = run_script(PYTHON_DIR / "models" / "sanity_check_factory.py")
        success = success and s1 and s2

    if step in ("4", "all"):
        print("\n>> Transpilando Arboles de Decision a C++ (.mqh)...")
        s = run_script(PYTHON_DIR / "models" / "export_factory_oracle.py")
        success = success and s

    if step in ("5",):
        print("\n>> Ejecutando Pipeline Institucional Completo...")
        s = run_script(PYTHON_DIR / "models" / "portfolio_factory.py")
        success = success and s

    return success


def run_interactive():
    """Interactive console menu loop."""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_header()
        print_menu()

        try:
            opcion = input("Seleccione una opcion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if opcion in ("1", "2", "3", "4", "5"):
            execute_step(opcion)
            try:
                input("\nPresiona Enter para volver al menu...")
            except (EOFError, KeyboardInterrupt):
                break
        elif opcion == "0":
            print("\nCerrando Panel de Control M2. Buen trading institucional!\n")
            break
        else:
            print("\n[-] Opcion no valida.")
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description="M2 Meta-Labeling Institutional CLI and Automated Pipeline Runner"
    )
    parser.add_argument(
        "--step",
        choices=["1", "2", "3", "4", "5", "all"],
        help="Execute a specific pipeline step non-interactively (1, 2, 3, 4, 5, or all)",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without prompting for input (defaults to --step all if --step is omitted)",
    )

    args = parser.parse_args()

    # Headless / Non-interactive invocation
    if args.step or args.non_interactive:
        step_to_run = args.step if args.step else "all"
        print_header()
        print(f"\n[MODO NO-INTERACTIVO] Ejecutando paso: {step_to_run}\n")
        success = execute_step(step_to_run)
        sys.exit(0 if success else 1)

    # Interactive invocation when launched without arguments
    run_interactive()


if __name__ == "__main__":
    main()

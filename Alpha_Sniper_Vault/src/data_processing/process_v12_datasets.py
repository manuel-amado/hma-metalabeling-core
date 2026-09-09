# =============================================================================
# process_v11_2_datasets.py -- Automated XGBoost Pipeline for V12
# Autor: Manuel & Antigravity (Protocolo V11.2)
#
# Descripción:
#   1. Busca automáticamente los archivos CSV generados por el Probador de Estrategias:
#      'Alpha_Sweep_Dataset_v12_<sym>.csv' en las carpetas de MT5 y locales.
#   2. Para cada símbolo encontrado:
#      a. Ejecuta 'train_universal.py' con Purga Institucional y bloques OOS ciegos.
#      b. Exporta el modelo optimizado (.pkl) a cabecera C++ / MQL5 (.mqh) usando 'export_model_to_mqh.py'.
#      c. Genera 'XGBoost_Model_v12_<sym>.mqh' sin sobrescribir los modelos V11.
#
# Uso:
#   cd C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src
#   ..\.venv\Scripts\python.exe process_v11_2_datasets.py [--watch]
# =============================================================================

import os
import sys
import io

# Configurar salida para soportar caracteres UTF-8 en consola de Windows (sin variable PYTHONUTF8=1)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import glob
import argparse
import subprocess
from datetime import datetime

# Rutas de búsqueda típicas donde MT5 Strategy Tester exporta los archivos CSV
SEARCH_ROOTS = [
    r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075",
    r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files",
    r"C:\Users\Manuel\Desktop\HMA_MetaLabeling",
    r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data",
    r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    os.path.abspath(os.path.dirname(__file__))
]

SYMBOLS = ["XAUUSD", "EURUSD", "USDJPY", "AUDUSD"]

def is_file_ready(filepath):
    try:
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
            return False
        with open(filepath, 'rb') as f:
            f.read(10)
        return True
    except (PermissionError, OSError):
        return False

def find_csv_for_symbol(sym):
    filename = f"Alpha_Sweep_Dataset_{sym}.csv"
    for root in SEARCH_ROOTS:
        if not os.path.exists(root):
            continue
        # Búsqueda rápida
        direct_path = os.path.join(root, filename)
        if is_file_ready(direct_path):
            return direct_path
        
        # Búsqueda recursiva en las subcarpetas del Tester / Agent-*
        matches = glob.glob(os.path.join(root, "**", filename), recursive=True)
        for match in matches:
            if is_file_ready(match):
                return match
    return None

def process_symbol(sym, csv_path):
    print("\n" + "="*70)
    print(f" [PROCESS] PROCESANDO MODELO XGBOOST V12: [{sym}]")
    print("="*70)
    print(f" -> Archivo CSV detectado: {csv_path}")
    print(f" -> Tamaño del dataset: {os.path.getsize(csv_path) / 1024.0:.2f} KB")

    src_dir = os.path.dirname(os.path.abspath(__file__))
    model_pkl = os.path.join(src_dir, "output", f"modelo_v12_{sym}.pkl")
    mqh_out = os.path.abspath(os.path.join(src_dir, "..", "mql5", f"XGBoost_Model_v12_{sym}_M15.mqh"))

    os.makedirs(os.path.dirname(model_pkl), exist_ok=True)

    # 1. Entrenar el modelo con purga y bloques OOS ciegos
    train_cmd = [
        sys.executable,
        os.path.join(src_dir, "train_universal.py"),
        "--data", csv_path,
        "--model", model_pkl
    ]
    print(f"\n[1/2] Entrenando árbol XGBoost institucional con Purga en {sym}...")
    res_train = subprocess.run(train_cmd, capture_output=True, text=True)
    if res_train.returncode != 0:
        print(f" [ERROR] Fallo en el entrenamiento de {sym}. Abortando transpilación.")
        print(" -> DETALLES DEL ERROR:\n")
        print(res_train.stderr)
        return False
    else:
        print(res_train.stdout)

    # 2. Transpilar el modelo .pkl a cabecera MQL5 (.mqh)
    export_cmd = [
        sys.executable,
        os.path.join(src_dir, "export_model_to_mqh.py"),
        "--model", model_pkl,
        "--output", mqh_out
    ]
    print(f"\n[2/2] Transpilando árboles a C++ / MQL5 en: {mqh_out}...")
    res_export = subprocess.run(export_cmd, capture_output=True, text=True)
    if res_export.returncode != 0:
        print(f" [ERROR] Fallo al generar el archivo .mqh para {sym}.")
        print(" -> DETALLES DEL ERROR:\n")
        print(res_export.stderr)
        return False
    else:
        print(res_export.stdout)

    print(f"\n [OK] ÉXITO: {sym} completado y exportado -> {mqh_out}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Pipeline Automático XGBoost V11.2 EXP")
    parser.add_argument("--watch", action="store_true", help="Supervisa en bucle la aparición de los nuevos archivos CSV.")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo en segundos para comprobar la carpeta en modo watch.")
    args = parser.parse_args()

    print("======================================================================")
    print(" [*] PIPELINE XGBOOST V12 - AUTO-DISCOVERY & COMPILER ")
    print("======================================================================")

    processed_symbols = set()

    while True:
        found_any = False
        for sym in SYMBOLS:
            if sym in processed_symbols:
                continue
            csv_path = find_csv_for_symbol(sym)
            if csv_path:
                found_any = True
                success = process_symbol(sym, csv_path)
                if success:
                    processed_symbols.add(sym)
        
        if len(processed_symbols) == len(SYMBOLS):
            print("\n [DONE] PROCESAMIENTO COMPLETO: Todos los símbolos han sido entrenados y exportados a .mqh.")
            break

        if not args.watch:
            if not found_any and len(processed_symbols) == 0:
                print("\n [INFO] No se encontraron archivos 'Alpha_Sweep_Dataset_v12_<symbol>.csv'.")
                print(" -> Cuando finalice el Probador de Estrategias de MT5 en 45 min, ejecuta este script para compilar los modelos.")
            else:
                print(f"\n [OK] Símbolos procesados en esta sesión: {list(processed_symbols)}")
            break
        else:
            print(f"\n [WATCH] {len(processed_symbols)}/{len(SYMBOLS)} completados. Esperando nuevos CSV (comprobando cada {args.interval}s)...")
            time.sleep(args.interval)

if __name__ == "__main__":
    main()

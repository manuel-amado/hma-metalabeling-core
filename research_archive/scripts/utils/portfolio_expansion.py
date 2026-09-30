import os
import shutil
import glob
import subprocess

DESKTOP_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
APPDATA_DIR = os.environ.get('APPDATA')
MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

def create_ini_file(symbol, period):
    ini_content = f"""[Tester]
Expert=Alpha_Sniper\\Alpha_Sniper_v8.ex5
Symbol={symbol}
Period={period}
Optimization=0
Model=4
FromDate=2015.01.01
ToDate=2026.07.01
Report={symbol}_Report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpMetaLabeling=1
InpFixedBalance=100000
InpSymbols={symbol}
"""
    ini_path = os.path.join(DESKTOP_DIR, "tester_auto.ini")
    with open(ini_path, "w") as f:
        f.write(ini_content)
    return ini_path

def harvest_csv(symbol):
    print(f"[*] Harvesting CSV for {symbol}...")
    search_paths = [
        os.path.join(APPDATA_DIR, "MetaQuotes", "Tester", "*", "Agent*", "MQL5", "Files", f"Alpha_Sweep_Dataset_{symbol}.csv"),
        os.path.join(APPDATA_DIR, "MetaQuotes", "Terminal", "*", "Tester", "Files", f"Alpha_Sweep_Dataset_{symbol}.csv")
    ]
    
    files = []
    for path in search_paths:
        files.extend(glob.glob(path))
    
    if not files:
        print("[-] Could not find generated CSV in Tester/Files.")
        return None
        
    latest_file = max(files, key=os.path.getmtime)
    dest_path = os.path.join(DESKTOP_DIR, f"Alpha_Sweep_Dataset_{symbol}.csv")
    
    shutil.copy2(latest_file, dest_path)
    print(f"[+] Harvested CSV to {dest_path}")
    return dest_path

def run_pipeline(symbol, timeframe):
    print(f"\n======================================")
    print(f"[*] Starting Pipeline for {symbol} {timeframe}")
    print(f"======================================")
    
    csv_path = os.path.join(DESKTOP_DIR, f"Alpha_Sweep_Dataset_{symbol}.csv")
    model_path = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", "src", "output", f"modelo_{symbol}_{timeframe}.pkl")
    
    venv_python = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", ".venv", "Scripts", "python.exe")
    train_script = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", "src", "train_universal.py")
    certify_script = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", "src", "certify_shuffle.py")
    export_script = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", "src", "export_model_to_mqh.py")
    mqh_path = os.path.join(DESKTOP_DIR, "Alpha_Sniper_Vault", "mql5", f"XGBoost_Model_{symbol}_{timeframe}.mqh")
    
    subprocess.run([venv_python, train_script, "--data", csv_path, "--model", model_path])
    subprocess.run([venv_python, certify_script, "--data", csv_path, "--model", model_path])
    subprocess.run([venv_python, export_script, "--model", model_path, "--output", mqh_path])

import time
import psutil

def wait_for_mt5_to_close():
    print("[*] Waiting for MT5 backtest to finish (terminal64.exe)...")
    time.sleep(5)  # Give it time to launch
    while True:
        mt5_procs = [p for p in psutil.process_iter(['name']) if p.info['name'] == "terminal64.exe"]
        if not mt5_procs:
            break
        time.sleep(5)

def run_autonomous_loop():
    assets = [
        ("AUDUSD", "M15"),
        ("AUDCAD", "M15")
    ]
    
    for symbol, period in assets:
        print(f"\n[>>>] INICIATING MT5 AUTONOMOUS BACKTEST FOR {symbol} {period}...")
        ini_path = create_ini_file(symbol, period)
        
        # Run MT5 (it detaches)
        subprocess.Popen([MT5_TERMINAL_PATH, f"/config:{ini_path}"])
        
        # Block until MT5 shuts itself down (ShutdownTerminal=1 in INI)
        wait_for_mt5_to_close()
        
        print(f"[+] MT5 Backtest for {symbol} finished. Harvesting data...")
        csv_path = harvest_csv(symbol)
        
        if csv_path:
            run_pipeline(symbol, period)

if __name__ == "__main__":
    run_autonomous_loop()

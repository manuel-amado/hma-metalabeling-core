import os
import subprocess
import time
import psutil
import glob
import re

DESKTOP_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
APPDATA_DIR = os.environ.get('APPDATA')
EA_PATH = r"Project_Hull_Apex\Hull_Apex_Bot.ex5"
SET_FILE = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\Hull_Apex_Opt.set"

MATRIX = {
    "FX_Majors": {
        "symbols": ["EURUSD", "GBPUSD"],
        "timeframes": ["M15", "H1"]
    },
    "Crypto": {
        "symbols": ["BTCUSD", "ETHUSD"],
        "timeframes": ["H1", "H4"]
    },
    "Indices": {
        "symbols": ["SPX500", "NAS100"],
        "timeframes": ["M30", "H1"]
    }
}

def wait_for_mt5_to_close():
    print("[*] Waiting for MT5 to finish backtest...")
    time.sleep(5)
    while True:
        mt5_procs = [p for p in psutil.process_iter(['name']) if p.info['name'] == 'terminal64.exe']
        if not mt5_procs:
            break
        time.sleep(5)

def run_headless_backtest(symbol, timeframe):
    print(f"\n======================================")
    print(f"[*] Running MULTISPECTRAL BACKTEST: {symbol} [{timeframe}]")
    print(f"======================================")
    
    report_name = f"Report_{symbol}_{timeframe}.xml"
    
    ini_content = f"""[Tester]
Expert={EA_PATH}
ExpertParameters={SET_FILE}
Symbol={symbol}
Period={timeframe}
Optimization=0
Model=4
Visual=0
FromDate=2018.01.01
ToDate=2026.07.01
ForwardMode=0
Report={report_name}
ReplaceReport=1
ShutdownTerminal=1
"""
    ini_path = os.path.join(DESKTOP_DIR, f"spectral_tester_{symbol}_{timeframe}.ini")
    with open(ini_path, "w") as f:
        f.write(ini_content)
        
    subprocess.Popen([MT5_TERMINAL_PATH, f"/config:{ini_path}"])
    wait_for_mt5_to_close()
    print(f"[+] Finished {symbol} {timeframe}. Report saved as {report_name}")

if __name__ == "__main__":
    print("🚀 INICIANDO PROTOCOLO APEX: EXPLORACIÓN ESPECTRAL V1.10")
    for category, config in MATRIX.items():
        print(f"\n---> Inicializando Cluster: {category}")
        for symbol in config["symbols"]:
            for tf in config["timeframes"]:
                run_headless_backtest(symbol, tf)
    print("\n✅ Misión Cumplida. Bucle Espectral Finalizado.")

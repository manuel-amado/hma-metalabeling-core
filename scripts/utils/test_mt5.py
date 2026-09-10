import os
import subprocess
import time
import psutil
import re

DESKTOP_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
APPDATA_DIR = os.environ.get('APPDATA')

def wait_for_mt5_to_close():
    print("[*] Waiting for MT5 to finish backtest...")
    time.sleep(5)
    while True:
        mt5_procs = [p for p in psutil.process_iter(['name']) if p.info['name'] == 'terminal64.exe']
        if not mt5_procs:
            break
        time.sleep(5)

def get_latest_agent_log():
    import glob
    search_path = os.path.join(APPDATA_DIR, "MetaQuotes", "Tester", "*", "Agent*", "logs", "*.log")
    files = glob.glob(search_path)
    if not files: return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

ini_content = f"""[Tester]
Expert=Project_Hull_Apex\\Hull_Apex_Bot.ex5
ExpertParameters=C:\\Users\\Manuel\\Desktop\\HMA_MetaLabeling\\Project_Hull_Apex\\Hull_Apex_Opt.set
Symbol=XAUUSD
Period=M15
Optimization=0
Model=0
FromDate=2024.01.01
ToDate=2024.03.01
Report=Hull_Test_Report.xml
ReplaceReport=1
ShutdownTerminal=1
"""
ini_path = os.path.join(DESKTOP_DIR, "hull_test.ini")
with open(ini_path, "w") as f:
    f.write(ini_content)

print("[*] Launching MT5...")
subprocess.Popen([MT5_TERMINAL_PATH, f"/config:{ini_path}"])
wait_for_mt5_to_close()

log_path = get_latest_agent_log()
if log_path:
    with open(log_path, 'r', encoding='utf-16', errors='ignore') as f:
        print(f.read()[-1000:])
else:
    print("[-] Log not found!")

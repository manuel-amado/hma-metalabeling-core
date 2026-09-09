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
    # MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\logs\
    import glob
    search_path = os.path.join(APPDATA_DIR, "MetaQuotes", "Tester", "*", "Agent*", "logs", "*.log")
    files = glob.glob(search_path)
    if not files: return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def parse_agent_log(log_path):
    with open(log_path, 'r', encoding='utf-16', errors='ignore') as f:
        content = f.read()
    
    np_match = re.search(r'Net Profit:\s+([\-\d\.]+)', content)
    dd_match = re.search(r'Max Drawdown \(\$\):\s+([\-\d\.]+)', content)
    pf_match = re.search(r'Profit Factor:\s+([\-\d\.]+)', content)
    
    np = np_match.group(1) if np_match else "N/A"
    dd = dd_match.group(1) if dd_match else "N/A"
    pf = pf_match.group(1) if pf_match else "N/A"
    return np, dd, pf

assets = ['USDJPY', 'AUDUSD', 'AUDCAD']

for symbol in assets:
    print(f"\n======================================")
    print(f"[*] Running LIVE BACKTEST for {symbol}")
    print(f"======================================")
    
    ini_content = f"""[Tester]
Expert=Alpha_Sniper\\Alpha_Sniper_v8.ex5
Symbol={symbol}
Period=M15
Optimization=0
Model=4
FromDate=2015.01.01
ToDate=2026.07.01
Report={symbol}_TEST.xml
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpMetaLabeling=0
InpEntryThreshold=0.508
InpFixedBalance=100000.0
InpRiskPerTrade=1.0
InpUseCompoundInterest=0
InpSymbols={symbol}
"""
    ini_path = os.path.join(DESKTOP_DIR, f"live_tester_{symbol}.ini")
    with open(ini_path, "w") as f:
        f.write(ini_content)
        
    subprocess.Popen([MT5_TERMINAL_PATH, f"/config:{ini_path}"])
    wait_for_mt5_to_close()
    
    log_path = get_latest_agent_log()
    if log_path:
        np, dd, pf = parse_agent_log(log_path)
        print(f"\n[+] RESULTS FOR {symbol}:")
        print(f"    - Net Profit:      {np}")
        print(f"    - Max Drawdown ($): {dd}")
        print(f"    - Profit Factor:   {pf}")
    else:
        print(f"[-] Log not found for {symbol}!")


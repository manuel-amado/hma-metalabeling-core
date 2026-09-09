import os

desktop = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
project_dir = os.path.join(desktop, "Project_Hull_Apex")

portfolio = [
    {"symbol": "XAUUSD", "tf": "M15", "set": "Hull_Apex_Opt.set", "desc": "Oro (Safe Haven)"},
    {"symbol": "BTCUSD", "tf": "H1", "set": "Apex_BTCUSD_H1.set", "desc": "Bitcoin (Cripto)"},
    {"symbol": "USDJPY", "tf": "H1", "set": "Apex_USDJPY_H1.set", "desc": "Yen (Forex Major)"}
]

bat_content = "@echo off\n"
bat_content += "echo ========================================================\n"
bat_content += "echo      SIMULADOR VISUAL: PORTAFOLIO DESCORRELACIONADO     \n"
bat_content += "echo ========================================================\n"
bat_content += "echo Seleccione el Activo a simular visualmente:\n"

for i, asset in enumerate(portfolio, 1):
    ini_name = f"Visual_Portafolio_{asset['symbol']}.ini"
    ini_path = os.path.join(project_dir, ini_name)
    set_path = os.path.join(desktop, "Alpha_Sniper_Vault", "Production", "Hull_Apex_v1.10", asset['set']) if asset['symbol'] != 'XAUUSD' else os.path.join(desktop, "Alpha_Sniper_Vault", "Production", "Hull_Apex_v1.10", "Apex_XAUUSD_M15.set")
    
    # Actually, XAUUSD uses Hull_Apex_Opt.set or I can just use the one in Project_Hull_Apex
    if asset['symbol'] == 'XAUUSD':
        set_path = os.path.join(desktop, "Project_Hull_Apex", "Hull_Apex_Opt.set")
        
    ini_content = f"""[Tester]
Expert=Project_Hull_Apex\\Hull_Apex_Bot.ex5
ExpertParameters={set_path}
Symbol={asset['symbol']}
Period={asset['tf']}
Optimization=0
Model=0
Visual=1
FromDate=2025.01.01
ToDate=2026.07.01
ForwardMode=0
ShutdownTerminal=0
"""
    with open(ini_path, "w") as f:
        f.write(ini_content)
        
    bat_content += f"echo {i}. {asset['symbol']} [{asset['tf']}] - {asset['desc']}\n"

bat_content += "echo ========================================================\n"
bat_content += "set /p choice=Ingrese el numero (1-3): \n\n"

for i, asset in enumerate(portfolio, 1):
    ini_name = f"Visual_Portafolio_{asset['symbol']}.ini"
    ini_path = os.path.join(project_dir, ini_name)
    bat_content += f"if \"%choice%\"==\"{i}\" (\n"
    bat_content += f"    echo Lanzando MetaTrader 5 para {asset['symbol']}...\n"
    bat_content += f"    \"C:\\Program Files\\MetaTrader 5\\terminal64.exe\" /config:{ini_path}\n"
    bat_content += f"    goto end\n"
    bat_content += f")\n"

bat_content += ":end\nexit\n"

bat_path = os.path.join(desktop, "Launch_Visual_Portfolio.bat")
with open(bat_path, "w") as f:
    f.write(bat_content)

print("[+] Portfolio visual setup completed successfully.")

import subprocess

metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
source = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp.log"

subprocess.run([metaeditor, f"/compile:{source}", f"/log:{log_path}"], capture_output=True)

try:
    with open(log_path, "r", encoding="utf-16") as f:
        print(f.read())
except Exception as e:
    print(f"Error reading log: {e}")
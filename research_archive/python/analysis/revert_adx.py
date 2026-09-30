import re
import subprocess

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Turn off ADX filter
text = re.sub(r'input bool\s+InpUseADXFilter\s*=\s*true;', 'input bool   InpUseADXFilter     = false;', text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

# Compile
metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp_revert.log"
subprocess.run([metaeditor, f"/compile:{file_path}", f"/log:{log_path}"], capture_output=True)

try:
    with open(log_path, "r", encoding="utf-16") as f:
        print(f.read())
except Exception as e:
    print(f"Log error: {e}")
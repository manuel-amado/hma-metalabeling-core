import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'input bool\s+InpExportMetaLabeling\s*=\s*false;', 'input bool   InpExportMetaLabeling = true;', text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

import subprocess
metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp_ml.log"
subprocess.run([metaeditor, f"/compile:{file_path}", f"/log:{log_path}"], capture_output=True)
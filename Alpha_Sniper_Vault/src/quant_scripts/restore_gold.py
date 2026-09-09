import re
import subprocess

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Restore Original Gold Defaults
text = re.sub(r'input int\s+InpHMA_Period\s*=\s*\d+;', 'input int    InpHMA_Period       = 200;', text)
text = re.sub(r'input double\s+InpMinDailyATR\s*=\s*[\d\.]+;', 'input double InpMinDailyATR      = 15.0;', text)
text = re.sub(r'input int\s+InpToxicStreakLevel\s*=\s*\d+;', 'input int    InpToxicStreakLevel = 8;', text)
text = re.sub(r'input int\s+InpPostWinCooldownBars\s*=\s*\d+;', 'input int    InpPostWinCooldownBars = 24;', text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

# Compile
metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp_restore.log"
subprocess.run([metaeditor, f"/compile:{file_path}", f"/log:{log_path}"], capture_output=True)

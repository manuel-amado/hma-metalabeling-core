import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Make sure Inputs are there
if "InpUseADXFilter" not in text[:2000]:
    target = 'input double InpMinDailyATR      = 15.0;'
    replacement = """input double InpMinDailyATR      = 15.0;

input group "=== Filtro de Regimen Macro ==="
input bool   InpUseADXFilter     = true;   // Activar filtro ADX Diario
input int    InpADXPeriod        = 14;     // Periodo del ADX
input double InpMinDailyADX      = 25.0;   // Valor minimo ADX para operar (Tendencia)
"""
    text = text.replace(target, replacement)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Inputs verified.")
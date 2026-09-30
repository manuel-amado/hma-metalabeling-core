import re
file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# 1. Add inputs
new_inputs = """input string srmm = "----------- Institutional Risk Engine (AGY) -----------";
input bool TradeLongs = true; // Habilitar Compras (Longs)
input bool TradeShorts = false; // Habilitar Ventas (Shorts) - Apagado por toxicidad estadistica
"""
code = code.replace('input string srmm = "----------- Institutional Risk Engine (AGY) -----------";\n', new_inputs)

# 2. Modify Long Entry
code = code.replace('if (_sqIsBarOpen == true && LongEntrySignal) {', 'if (_sqIsBarOpen == true && LongEntrySignal && TradeLongs) {')

# 3. Modify Short Entry
code = code.replace('if (_sqIsBarOpen == true && (ShortEntrySignal && !LongEntrySignal)) {', 'if (_sqIsBarOpen == true && (ShortEntrySignal && !LongEntrySignal) && TradeShorts) {')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Directional toggles added.')

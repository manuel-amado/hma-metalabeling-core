file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace('input group "=== Filtro Macro Inter-Mercado (DXY) ===\n', 'input group "=== Filtro Macro Inter-Mercado (DXY) ==="\n')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Syntax fixed.")
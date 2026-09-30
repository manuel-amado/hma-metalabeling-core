import re

file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Habilitar Shorts para descubrir si GBPJPY tiene edge direccional bajista
code = re.sub(
    r'input\s+bool\s+TradeShorts\s*=\s*false;\s*//.*',
    'input bool TradeShorts = true; // Habilitar Ventas (Shorts) para Extraccion Multi-Activo',
    code
)

# Ampliar el Max Spread a 9999 para que no bloquee trades validos durante el backtest de extraccion
code = re.sub(
    r'input\s+int\s+MaxSpreadPoints\s*=\s*\d+;\s*//.*',
    'input int MaxSpreadPoints = 9999; // Max Spread abierto para extraer el 100% de señales',
    code
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Pipeline_Extractor_M1.mq5 optimizado para GBPJPY (y cualquier otro activo).")

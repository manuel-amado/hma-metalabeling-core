import re
import os

base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery'
files = ['Pipeline_Extractor_M1.mq5', 'Strategy 2.91.69.mq5']

for file_name in files:
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Regex para encontrar correctSymbol y reemplazar su contenido
    pattern = r'string\s+correctSymbol\s*\(\s*string\s+symbol\s*\)\s*\{[\s\S]*?\}'
    replacement = 'string correctSymbol(string symbol){\n    return _Symbol; // BLOQUEO HARDWARE CONTRA CACHE DE TESTER\n}'
    
    new_code = re.sub(pattern, replacement, code)
    
    # También forzamos MaxSpreadPoints a 9999 en el Extractor para asegurar que no se salte nada
    if 'Extractor' in file_name:
        new_code = re.sub(r'input\s+int\s+MaxSpreadPoints\s*=\s*\d+\s*;', 'input int MaxSpreadPoints = 9999;', new_code)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_code)

print("Parche radical inyectado. correctSymbol ahora fuerza _Symbol en todo momento.")

import re

file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Forzar el Deals CSV al directorio común compartiendo la bandera FILE_COMMON
code = re.sub(
    r'int\s+handle\s*=\s*FileOpen\s*\(\s*filename\s*,\s*FILE_CSV\s*\|\s*FILE_WRITE\s*\|\s*FILE_READ\s*,\s*";"\s*\)\s*;',
    'int handle = FileOpen(filename, FILE_CSV|FILE_WRITE|FILE_READ|FILE_COMMON, ";");',
    code
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Parche FILE_COMMON aplicado con exito. Archivos listos para batch.")

import re

file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Modificar la definición global de xgbCsvFileName
code = re.sub(
    r'string\s+xgbCsvFileName\s*=\s*"[^"]+";',
    'string xgbCsvFileName = ""; // Se inicializara en OnInit con el simbolo',
    code
)

# 2. Inyectar la asignación dinámica en OnInit()
# Buscamos OnInit() y añadimos la línea justo después
oninit_pattern = r'(int\s+OnInit\s*\(\s*\)\s*\{)'
replacement = r'\1\n    xgbCsvFileName = "XGBoost_Features_M1_" + _Symbol + ".csv";'
if 'xgbCsvFileName = "XGBoost_Features_M1_" + _Symbol' not in code:
    code = re.sub(oninit_pattern, replacement, code, count=1)

# 3. Modificar writeReportFile
code = re.sub(
    r'string\s+filename\s*=\s*MQLInfoString\(MQL_PROGRAM_NAME\)\s*\+\s*"\.csv";',
    r'string filename = MQLInfoString(MQL_PROGRAM_NAME) + "_" + _Symbol + ".csv";',
    code
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Pipeline_Extractor_M1.mq5 parcheado con nombres de archivos dinámicos (_Symbol).")

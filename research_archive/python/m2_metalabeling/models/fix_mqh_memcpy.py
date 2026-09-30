import re

paths = [
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\M2_XGBoost_Oracle.mqh',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Include\M2_XGBoost_Oracle.mqh'
]

for p in paths:
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    # Generic replace for memcpy(output, ...) or memcpy(result, ...)
    code = re.sub(
        r'memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;',
        r'result[0] = \1;\n    result[1] = \2;',
        code
    )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(code)

print("M2_XGBoost_Oracle.mqh fixed!")

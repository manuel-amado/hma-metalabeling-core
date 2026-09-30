import re

target_file = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'
with open(target_file, 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'#include\s*[\"<]M2_XGBoost_Oracle\.mqh[\">]\s*\n?', '', code)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(code)
print('Oracle include removed.')

import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'MIN_TRADES        = 300'
replacement = 'MIN_TRADES        = 100'

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Reduced MIN_TRADES to 100')

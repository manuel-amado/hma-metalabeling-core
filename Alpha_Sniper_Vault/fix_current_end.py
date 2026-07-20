import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "current_end = start_date + pd.DateOffset(months=60)"
replacement = "current_end = start_date + pd.DateOffset(months=12) # Reduced to 1 year for Phase 41"

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Reduced current_end to 1 year')

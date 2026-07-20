import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "start_date = df_clean['Time'].min() + pd.DateOffset(years=5)"
replacement = "start_date = df_clean['Time'].min() + pd.DateOffset(years=1) # Reduced to 1 year for Phase 41"

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Reduced WFO initial window to 1 year')

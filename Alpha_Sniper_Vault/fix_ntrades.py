import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'df_stable = df_results[df_results["n_trades"] >= 300]'
replacement = 'df_stable = df_results[df_results["n_trades"] >= 100]'

content = content.replace(target, replacement)

target2 = 'print(f"  Combinaciones validas (>=300 trades): {len(df_stable)}")'
replacement2 = 'print(f"  Combinaciones validas (>=100 trades): {len(df_stable)}")'

content = content.replace(target2, replacement2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Reduced min trades to 100')

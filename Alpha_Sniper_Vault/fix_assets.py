import os

file_path = r'src\pipeline_global_optimizer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'csv_files = [os.path.join(DATA_DIR, "Struct_Dataset_XAUUSD.csv")]'
replacement = '''assets = ["EURUSD", "USDJPY", "GBPUSD", "EURJPY"]
    csv_files = [os.path.join(DATA_DIR, f"Struct_Dataset_{a}.csv") for a in assets]'''
content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Set assets to EURUSD, USDJPY, GBPUSD, EURJPY')

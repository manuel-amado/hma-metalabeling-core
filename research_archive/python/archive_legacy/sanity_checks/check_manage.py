import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_manage = False
for i, line in enumerate(lines):
    if 'void ManageOpenTrades' in line:
        in_manage = True
    if in_manage:
        print(f"{i}: {line.strip()}")
        if 'int total_magic_pos' in line:
            break
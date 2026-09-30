import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"Alpha_Sweep_Dataset_v15_1_"', '"Alpha_Sweep_Dataset_v17_"')
content = content.replace('"Alpha_Sweep_Dataset_v16_1_"', '"Alpha_Sweep_Dataset_v17_"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Filename patched to v17")
import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace cur_time with TimeCurrent()
content = content.replace('TimeToStruct(cur_time, dt_curr);', 'TimeToStruct(TimeCurrent(), dt_curr);')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Error 'cur_time' corregido en Alpha_Sniper_v17.mq5")
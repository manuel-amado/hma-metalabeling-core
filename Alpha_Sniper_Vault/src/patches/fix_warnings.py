import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v20.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = "double hma_exit[2], rsi_buf[1], stddev[2], sma20[2], atr_d1_buf[1];"
new_decl = "double hma_exit[], rsi_buf[], stddev[], sma20[], atr_d1_buf[];"

content = content.replace(target, new_decl)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Warnings patched.")
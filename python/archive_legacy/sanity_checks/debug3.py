import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        if(!has_trigger) {
            lastBarTime = currentBarTime;
            return;
        }"""

new_code = """        if(!has_trigger) {
            static int debug_count = 0;
            if(debug_count < 5) {
                Print("DEBUG: No trigger. HMA: ", hma_entry[1], ", ", hma_entry[2], ", ", hma_entry[3]);
                debug_count++;
            }
            lastBarTime = currentBarTime;
            return;
        }"""

content = content.replace(target, new_code)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("HMA values debug added.")
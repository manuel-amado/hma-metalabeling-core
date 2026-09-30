import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix warning: change static arrays to dynamic arrays
target_decl = "double hma_entry_chk[2], rsi_buf[1], stddev[1], sma20[1], atr_d1_buf[1];"
new_decl = "double hma_entry_chk[], rsi_buf[], stddev[], sma20[], atr_d1_buf[];"
content = content.replace(target_decl, new_decl)

# Remove the faulty velocity calculation that uses the undefined hma_exit array
vel_block = """        double exit_hma_velocity = 0.0;
        if(current_atr > 0) exit_hma_velocity = (hma_exit[0] - hma_exit[1]) / current_atr;
        double exit_hma_accel = 0.0;"""
new_vel_block = """        double exit_hma_velocity = 0.0;
        double exit_hma_accel = 0.0;"""

content = content.replace(vel_block, new_vel_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Bugs patched!")
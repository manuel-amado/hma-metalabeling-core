import os
filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_V20_Dynamic.mq5'
with open(filepath, 'r') as f:
    content = f.read()

# Remove the early returns
old_returns = '''    if(!MQLInfoInteger(MQL_TESTER) && PositionsTotal() > 0) return; // Simple logic: 1 trade max
    if(MQLInfoInteger(MQL_TESTER) && PositionsTotal() > 0) return;'''
content = content.replace(old_returns, '')

# Add the position check right before trade execution
old_exec = '''        if(prob >= InpAI_Threshold) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);'''

new_exec = '''        if(prob >= InpAI_Threshold && PositionsTotal() == 0) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);'''

content = content.replace(old_exec, new_exec)
with open(filepath, 'w') as f:
    f.write(content)

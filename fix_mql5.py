filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19_WFO.mq5'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('double sym_entry_thresh = 0.50;', 'double sym_entry_thresh = 0.0; // V19 EV Threshold (0.0 means take any positive EV trade)')
content = content.replace('if(InpEntryThreshold > 0.0) sym_entry_thresh = InpEntryThreshold;', 'if(InpEntryThreshold != 0.0) sym_entry_thresh = InpEntryThreshold;')

with open(filepath, 'w') as f:
    f.write(content)
print("MQL5 fixed")

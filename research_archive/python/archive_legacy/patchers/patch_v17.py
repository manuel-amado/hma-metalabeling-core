import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"SignalType,HMAAccelF', '"Time,SignalType,HMAAccelF')

old_format = 'StringFormat("%.2f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%d\\n"'
new_format = 'StringFormat("%s,%.2f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%d\\n", TimeToString(currentBarTime, TIME_DATE|TIME_MINUTES)'
content = content.replace(old_format, new_format)

old_print = 'Print("Rechazado por XGBoost. Proba: ", entry_proba, " < ", sym_entry_thresh);'
new_print = 'Print("[", m_symbol, "] Rechazado por XGBoost. Proba: ", entry_proba, " < ", sym_entry_thresh);'
content = content.replace(old_print, new_print)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch V17 success")
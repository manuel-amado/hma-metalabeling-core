import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        if(signalType != -1) {
            if(false) {
                Print("ABORT: Spread demasiado alto en ", m_symbol, " - Spread: ", spread, " Max: ", max_allowed_spread);
                lastBarTime = currentBarTime;
                return;
            }"""

new_code = """        if(signalType != -1) {
            Print("DEBUG: SIGNAL DETECTED. Type: ", signalType);
            if(false) {
                Print("ABORT: Spread demasiado alto en ", m_symbol, " - Spread: ", spread, " Max: ", max_allowed_spread);
                lastBarTime = currentBarTime;
                return;
            }"""

content = content.replace(target, new_code)

target2 = """                double lots = CalcDynamicLotSize(signalType, open_p, sl);
                string comment = "AI_" + DoubleToString(entry_proba, 2);
                
                if(lots > 0) {"""

new_code2 = """                double lots = CalcDynamicLotSize(signalType, open_p, sl);
                string comment = "AI_" + DoubleToString(entry_proba, 2);
                
                Print("DEBUG: Calculated Lots: ", lots);
                
                if(lots > 0) {"""

content = content.replace(target2, new_code2)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Signal debugs added.")
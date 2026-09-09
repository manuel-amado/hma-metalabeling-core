import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Bypass ML restriction
target_ml = """        else {
            PrintFormat("ABORTO CRITICO: Simbolo [%s] NO posee modelo WFO.", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }"""
new_ml = """        else {
            // MODO EXPLORADOR: Para Crypto e Indices, si no hay ML, operamos la raw-mechanic.
            entry_proba = 1.0; 
            sym_entry_thresh = 0.5;
        }"""
content = content.replace(target_ml, new_ml)

# 2. Bypass Spread Filter for Crypto/Indices
target_spread = """        double sl_pips = sl_dist / GetPip();
        
        if(spread_pips > MaxSpreadPips) {
            Print("ABORT: Spread demasiado alto: ", spread_pips, " pips");
            lastBarTime = currentBarTime; return; 
        }"""
new_spread = """        double sl_pips = sl_dist / GetPip();
        
        // MODO EXPLORADOR: Desactivamos el filtro de spread para activos no-Forex
        bool is_forex = (StringFind(m_symbol, "USD") != -1 && StringLen(m_symbol) <= 7 && m_symbol != "BTCUSD" && m_symbol != "US30");
        if(is_forex && spread_pips > MaxSpreadPips) {
            Print("ABORT: Spread demasiado alto: ", spread_pips, " pips");
            lastBarTime = currentBarTime; return; 
        }"""
content = content.replace(target_spread, new_spread)

# 3. Fix the "InpSymbols" input so it doesn't restrict
# Actually, the user selects the symbol in the tester, but we should make sure the EA handles it.

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("V21 Explorador Patched.")
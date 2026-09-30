import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v18_WFO.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscamos la funcion GetSymbolThreshold y la eliminamos entera
target_func = """double GetSymbolThreshold(string symbol_name) {
   if(InpEntryThreshold > 0.0) return InpEntryThreshold;
   
   if(symbol_name == "XAUUSD") return XGBOOST_THRESHOLD_XAUUSD;
   if(symbol_name == "EURUSD") return XGBOOST_THRESHOLD_EURUSD;
   if(symbol_name == "USDJPY") return XGBOOST_THRESHOLD_USDJPY;
   if(symbol_name == "AUDUSD") return 0.50;
   
   return 0.50; // Fallback
}"""

if target_func in content:
    content = content.replace(target_func, "")
else:
    print("Function not found exactly as expected. Let's try regex.")
    import re
    content = re.sub(r'double GetSymbolThreshold\(string symbol_name\) \{.*?\return 0\.50; // Fallback\s*\}', '', content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v18_WFO.mq5 parcheado con exito.")
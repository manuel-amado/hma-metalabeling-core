import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix threshold names back to what the exporter actually writes
content = content.replace("XGBOOST_THRESHOLD_v17_XAUUSD", "XGBOOST_THRESHOLD_XAUUSD")
content = content.replace("XGBOOST_THRESHOLD_v17_EURUSD", "XGBOOST_THRESHOLD_EURUSD")
content = content.replace("XGBOOST_THRESHOLD_v17_USDJPY", "XGBOOST_THRESHOLD_USDJPY")
content = content.replace("XGBOOST_THRESHOLD_v17_AUDUSD", "XGBOOST_THRESHOLD_AUDUSD")

# Remove AUDUSD from includes
content = content.replace('#include "XGBoost_Model_v17_AUDUSD_M15.mqh"', '//#include "XGBoost_Model_v17_AUDUSD_M15.mqh"')

# Fix AUDUSD fallback in GetSymbolThreshold
content = content.replace('if(symbol_name == "AUDUSD") return XGBOOST_THRESHOLD_AUDUSD;', 'if(symbol_name == "AUDUSD") return 0.50;')

# Fix AUDUSD fallback in prediction routing
content = content.replace('else if(m_symbol == "AUDUSD") entry_proba = XGBoost_Predict_v17_AUDUSD(features);', 'else if(m_symbol == "AUDUSD") entry_proba = 0.0; // AUDUSD disabled in V17')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v17.mq5 AUDUSD and thresholds patched.")
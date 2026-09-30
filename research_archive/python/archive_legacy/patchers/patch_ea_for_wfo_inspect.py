import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace include headers
new_includes = """
#include "XGBoost_Model_WFO_XAUUSD.mqh"
#include "XGBoost_Model_WFO_EURUSD.mqh"
#include "XGBoost_Model_WFO_USDJPY.mqh"
"""
# Find existing includes (it varies, let's just replace the block)
import re
content = re.sub(r'#include "XGBoost_Model_v17_[^\n]*\n', '', content)
content = content.replace('//--- Includes', '//--- Includes\n' + new_includes)

# Replace the GetMLPrediction logic
target = """
   if(symbol_name == "XAUUSD") return XGBOOST_THRESHOLD_XAUUSD;
   if(symbol_name == "EURUSD") return XGBOOST_THRESHOLD_EURUSD;
   if(symbol_name == "USDJPY") return XGBOOST_THRESHOLD_USDJPY;
   if(symbol_name == "AUDUSD") return 0.50;
"""
# We don't need a static threshold getter anymore if we return it via reference!
# But wait, the EA structure calls GetMLThreshold() and GetMLPrediction().
# Let's see how the EA calls them.
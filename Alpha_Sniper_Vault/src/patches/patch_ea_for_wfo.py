import os
import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Includes
content = re.sub(r'#include "XGBoost_Model_v17_XAUUSD_M15\.mqh"', '#include "XGBoost_Model_WFO_XAUUSD.mqh"', content)
content = re.sub(r'#include "XGBoost_Model_v17_EURUSD_M15\.mqh"', '#include "XGBoost_Model_WFO_EURUSD.mqh"', content)
content = re.sub(r'#include "XGBoost_Model_v17_USDJPY_M15\.mqh"', '#include "XGBoost_Model_WFO_USDJPY.mqh"', content)

# 2. Prediction logic inside CSymbolManager::CheckEntry
target_predict = """        double entry_proba = 0.0;
        if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_v17_XAUUSD(features);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_v17_EURUSD(features);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_v17_USDJPY(features);
        else if(m_symbol == "AUDUSD") entry_proba = 0.0; // AUDUSD disabled in V17

        
        bool execute_trade = false;
        double sym_entry_thresh = GetSymbolThreshold(m_symbol);"""

new_predict = """        double entry_proba = 0.0;
        double sym_entry_thresh = 0.50;
        
        MqlDateTime dt_wfo;
        TimeToStruct(TimeCurrent(), dt_wfo);
        int current_year = dt_wfo.year;

        if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_WFO_XAUUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_EURUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_USDJPY(features, current_year, sym_entry_thresh);
        else if(m_symbol == "AUDUSD") entry_proba = 0.0; // AUDUSD disabled in V17
        
        if(InpEntryThreshold > 0.0) sym_entry_thresh = InpEntryThreshold;

        bool execute_trade = false;"""

content = content.replace(target_predict, new_predict)

# 3. Save as Alpha_Sniper_v18_WFO.mq5
out_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v18_WFO.mq5'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v18_WFO.mq5 created successfully.")
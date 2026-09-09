import os
import shutil
import re

source = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v11_3.mq5'
target = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19.mq5'

shutil.copy(source, target)

with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update includes
content = re.sub(r'#include "XGBoost_Model_[^\n]*\n', '', content)
# It might have multiple, so let's just insert after a specific marker or at the top of includes
content = re.sub(r'(#include "HMA_FUNCTIONS\.mqh"\s*\n)', r'\1#include "XGBoost_Model_WFO_v19_XAUUSD.mqh"\n#include "XGBoost_Model_WFO_v19_EURUSD.mqh"\n#include "XGBoost_Model_WFO_v19_USDJPY.mqh"\n', content)

# 2. Update prediction block
target_predict = """        double entry_proba = 0.0;
        if(m_symbol == "XAUUSD")      entry_proba = XGBoost_Predict_XAUUSD(features);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_EURUSD(features);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_USDJPY(features);
        else if(m_symbol == "AUDUSD") entry_proba = XGBoost_Predict_AUDUSD(features);
        else if(m_symbol == "AUDCAD") entry_proba = XGBoost_Predict_AUDCAD(features);
        else if(m_symbol == "GBPJPY") entry_proba = XGBoost_Predict_GBPJPY(features);
        else if(m_symbol == "XAGUSD") entry_proba = XGBoost_Predict_XAGUSD(features);
        else {
            PrintFormat("  [PROTOCOLO V9.1] ABORTO CRITICO: Simbolo [%s] NO posee modelo XGBoost nativo. Fallback a XAUUSD bloqueado por seguridad.", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }
        
        bool execute_trade = false;
        double sym_entry_thresh = GetSymbolThreshold(m_symbol);"""

new_predict = """        double entry_proba = 0.0;
        double sym_entry_thresh = 0.50;
        
        MqlDateTime dt_wfo;
        TimeToStruct(TimeCurrent(), dt_wfo);
        int current_year = dt_wfo.year;

        if(m_symbol == "XAUUSD")      entry_proba = XGBoost_Predict_WFO_v19_XAUUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_v19_EURUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_v19_USDJPY(features, current_year, sym_entry_thresh);
        else {
            PrintFormat("ABORTO CRITICO: Simbolo [%s] NO posee modelo WFO.", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }
        
        if(InpEntryThreshold > 0.0) sym_entry_thresh = InpEntryThreshold;

        bool execute_trade = false;"""

content = content.replace(target_predict, new_predict)

# 3. Remove GetSymbolThreshold function
content = re.sub(r'double GetSymbolThreshold\(string symbol_name\) \{.*?\return 0\.50; // Fallback\s*\}', '', content, flags=re.DOTALL)

# 4. Remove any hardcoded AUDUSD references if necessary (not strictly needed since we just handled it in the if block)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v19.mq5 generated and patched.")
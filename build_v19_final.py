filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19_WFO.mq5'
with open(filepath, 'r') as f:
    content = f.read()

# Add current_month
content = content.replace('int current_year = dt_wfo.year;', 'int current_year = dt_wfo.year;\n        int current_month = dt_wfo.mon;')

# Fix Routing
old_routing = '''        // Routing disabled in v19 for extraction
        // if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_WFO_v19_XAUUSD(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_v19_EURUSD(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_v19_USDJPY(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "AUDUSD") entry_proba = 0.0;'''

new_routing = '''        if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_WFO_v19_XAUUSD(features, current_year, current_month, sym_entry_thresh);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_v19_EURUSD(features, current_year, current_month, sym_entry_thresh);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_v19_USDJPY(features, current_year, current_month, sym_entry_thresh);
        else if(m_symbol == "AUDUSD") entry_proba = XGBoost_Predict_WFO_v19_AUDUSD(features, current_year, current_month, sym_entry_thresh);'''

content = content.replace(old_routing, new_routing)

# Fix Includes
old_includes = '''//#include "Models\XGBoost_Model_WFO_v19_XAUUSD.mqh"
//#include "Models\XGBoost_Model_WFO_v19_EURUSD.mqh"
//#include "Models\XGBoost_Model_WFO_v19_USDJPY.mqh"'''

new_includes = '''#include "Models\XGBoost_Model_WFO_v19_XAUUSD.mqh"
#include "Models\XGBoost_Model_WFO_v19_EURUSD.mqh"
#include "Models\XGBoost_Model_WFO_v19_USDJPY.mqh"
#include "Models\XGBoost_Model_WFO_v19_AUDUSD.mqh"'''

content = content.replace(old_includes, new_includes)

with open(filepath, 'w') as f:
    f.write(content)
print("V19 Final Code Applied")

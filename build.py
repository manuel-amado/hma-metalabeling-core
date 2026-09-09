filepath_in = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v18_WFO.mq5'
filepath_out = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19_WFO.mq5'
with open(filepath_in, 'r') as f:
    content = f.read()

content = content.replace('double m_saved_features[26];', 'double m_saved_features[29];')
content = content.replace('f < 26; f++', 'f < 29; f++')
content = content.replace('double features[26];', 'double features[29];')

feature_assignment_str = '''        double runway_hma200 = 0;
        if(current_atr > 0) runway_hma200 = (signalType == 0) ? (hma200_buf[1] - rates[1].close) / current_atr : (rates[1].close - hma200_buf[1]) / current_atr;
        features[24] = runway_hma200;
        features[25] = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;'''

new_feature_str = '''        double runway_hma200 = 0;
        if(current_atr > 0) runway_hma200 = (signalType == 0) ? (hma200_buf[1] - rates[1].close) / current_atr : (rates[1].close - hma200_buf[1]) / current_atr;
        features[24] = runway_hma200;
        features[25] = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
        
        // --- V19 NEW FEATURES ---
        // 1. Time Mapping (Session cycles)
        MqlDateTime dt_feat;
        TimeToStruct(rates[1].time, dt_feat);
        double minutes_of_day = (double)dt_feat.hour * 60.0 + (double)dt_feat.min;
        features[26] = MathSin(2.0 * 3.14159265358979323846 * minutes_of_day / 1440.0);
        features[27] = MathCos(2.0 * 3.14159265358979323846 * minutes_of_day / 1440.0);
        
        // 2. Pain Index (Drawdown from 10-day High / Drawup from 10-day Low)
        int highest_idx = iHighest(m_symbol, _Period, MODE_HIGH, 960, 1);
        int lowest_idx = iLowest(m_symbol, _Period, MODE_LOW, 960, 1);
        double hh_10d = iHigh(m_symbol, _Period, highest_idx);
        double ll_10d = iLow(m_symbol, _Period, lowest_idx);
        double pain_index = 0.0;
        if(current_atr > 0) {
            if(signalType == 0) { // BUY
                pain_index = (hh_10d - rates[1].close) / current_atr; 
            } else { // SELL
                pain_index = (rates[1].close - ll_10d) / current_atr;
            }
        }
        features[28] = pain_index;'''

content = content.replace(feature_assignment_str, new_feature_str)
content = content.replace('Alpha_Sniper_v18_WFO', 'Alpha_Sniper_v19_WFO')

routing_str = '''        if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_WFO_XAUUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_EURUSD(features, current_year, sym_entry_thresh);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_USDJPY(features, current_year, sym_entry_thresh);
        else if(m_symbol == "AUDUSD") entry_proba = 0.0; // AUDUSD disabled in V17'''

new_routing_str = '''        // Routing disabled in v19 for extraction
        // if(m_symbol == "XAUUSD") entry_proba = XGBoost_Predict_WFO_v19_XAUUSD(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_WFO_v19_EURUSD(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_WFO_v19_USDJPY(features, current_year, sym_entry_thresh);
        // else if(m_symbol == "AUDUSD") entry_proba = 0.0;'''

content = content.replace(routing_str, new_routing_str)

includes_str = '''#include "Models\XGBoost_Model_WFO_XAUUSD.mqh"
#include "Models\XGBoost_Model_WFO_EURUSD.mqh"
#include "Models\XGBoost_Model_WFO_USDJPY.mqh"'''

new_includes_str = '''//#include "Models\XGBoost_Model_WFO_v19_XAUUSD.mqh"
//#include "Models\XGBoost_Model_WFO_v19_EURUSD.mqh"
//#include "Models\XGBoost_Model_WFO_v19_USDJPY.mqh"'''

content = content.replace(includes_str, new_includes_str)
content = content.replace('ArraySize(features) != 26', 'ArraySize(features) != 29')

with open(filepath_out, 'w') as f:
    f.write(content)
print("Done")

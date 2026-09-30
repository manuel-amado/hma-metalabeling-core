import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSymbolManager class definition back to 26
content = content.replace('double m_saved_features[22];', 'double m_saved_features[26];')

# 2. Update CSV row loop back to 26
content = content.replace('for(int f = 0; f < 22; f++) row += StringFormat("%f,", m_saved_features[f]);', 'for(int f = 0; f < 26; f++) row += StringFormat("%f,", m_saved_features[f]);')

# 3. Restore the prediction features array population to 26 variables
new_features_block = """
        // V17: Array de 22 features (esterilizado de variables basura)
        double features[22];
        features[0]  = signalType;
        features[1]  = hma_accel_feat;
        features[2]  = mtf_atr_ratio;
        features[3]  = dist_synth_h4;
        features[4]  = candle_dominance;
        features[5]  = twap_z_score;
        features[6]  = atr_ratio_high;
        features[7]  = rsi_buf[0];
        features[8]  = dist_asian_high_atr;
        features[9]  = dist_asian_low_atr;
        features[10] = rsi_extreme;
        features[11] = vol_spread_ratio;
        features[12] = trigger_rejection_tail;
        features[13] = ribbon_spread_stddev;
        features[14] = feat_ribbon_align;
        features[15] = feat_opposite_bars;
        features[16] = atr_d1_buf[0];
        features[17] = adx_buf[0];
        features[18] = feat_price_dev_atr;
        features[19] = (double)build_up_length;
        
        double runway_hma200 = 0;
        if(current_atr > 0) runway_hma200 = (signalType == 0) ? (hma200_buf[1] - rates[1].close) / current_atr : (rates[1].close - hma200_buf[1]) / current_atr;
        features[20] = runway_hma200;
        features[21] = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
"""

old_features_block = """
        // V17 (Restaurado a V16.1): Array de 26 features completas
        double features[26];
        features[0]  = signalType;
        features[1]  = hma_accel_feat;
        features[2]  = mtf_atr_ratio;
        features[3]  = dist_synth_h4;
        features[4]  = candle_dominance;
        features[5]  = twap_z_score;
        features[6]  = atr_ratio_high;
        features[7]  = rsi_buf[0];
        features[8]  = dist_asian_high_atr;
        features[9]  = dist_asian_low_atr;
        features[10] = rsi_extreme;
        features[11] = vol_spread_ratio;
        features[12] = spread;
        features[13] = trigger_rejection_tail;
        features[14] = ribbon_spread_stddev;
        features[15] = feat_ribbon_align;
        features[16] = feat_vpivot_monotonic;
        features[17] = feat_rsi_memory;
        features[18] = feat_opposite_bars;
        features[19] = atr_d1_buf[0];
        features[20] = adx_buf[0];
        features[21] = feat_price_dev_atr;
        features[22] = (double)build_up_length;
        features[23] = (double)pandas_dow;
        double runway_hma200 = 0;
        if(current_atr > 0) runway_hma200 = (signalType == 0) ? (hma200_buf[1] - rates[1].close) / current_atr : (rates[1].close - hma200_buf[1]) / current_atr;
        features[24] = runway_hma200;
        features[25] = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
"""

if "double features[22];" in content:
    content = content.replace(new_features_block.strip(), old_features_block.strip())

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Features array restored to 26 in Alpha_Sniper_v17.mq5.")
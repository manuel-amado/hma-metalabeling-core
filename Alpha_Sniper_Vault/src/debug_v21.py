import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add debug prints to all CopyBuffer calls in ProcessTick
target = """        int rates_copied    = CopyRates(m_symbol, _Period, 0, 60, rates);
        if(rates_copied < 4) return;
        ArraySetAsSeries(rates, true); // ANCLAJE FORZOSO PARA MANTENER LA SERIE TEMPORAL
        int hma_copied      = CopyBuffer(hma_entry_handle,      0, 0, 60, hma_entry);
        if(hma_copied < 4)   return;
        ArraySetAsSeries(hma_entry, true);   // ANCLAJE FORZOSO PARA MANTENER LA SERIE TEMPORAL
        int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
        if(hma_exit_copied < 3) return;"""

new_code = """        int rates_copied    = CopyRates(m_symbol, _Period, 0, 60, rates);
        if(rates_copied < 4) { Print("DEBUG: CopyRates rates failed"); return; }
        ArraySetAsSeries(rates, true);
        int hma_copied      = CopyBuffer(hma_entry_handle,      0, 0, 60, hma_entry);
        if(hma_copied < 4) { Print("DEBUG: CopyBuffer hma_entry failed");  return; }
        ArraySetAsSeries(hma_entry, true);
        int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
        if(hma_exit_copied < 3) { Print("DEBUG: CopyBuffer hma_exit failed"); return; }"""

content = content.replace(target, new_code)

target_multi = """        if(CopyBuffer(ribbon_hma10, 0, 0, 20, hma10_buf) < 20) return; ArraySetAsSeries(hma10_buf, true);
        if(CopyBuffer(ribbon_hma21, 0, 0, 20, hma21_buf) < 20) return; ArraySetAsSeries(hma21_buf, true);
        if(CopyBuffer(ribbon_hma50, 0, 0, 20, hma50_buf) < 20) return; ArraySetAsSeries(hma50_buf, true);
        if(CopyBuffer(ribbon_hma100, 0, 0, 20, hma100_buf) < 20) return; ArraySetAsSeries(hma100_buf, true);
        if(CopyBuffer(ribbon_hma200, 0, 0, 20, hma200_buf) < 20) return; ArraySetAsSeries(hma200_buf, true);
        if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
        if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) return;
        if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) return;
        if(CopyBuffer(atr_d1_handle,  0, 1, 1,  atr_d1_buf) < 1) return;
        if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  return;
        if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  return;"""

new_multi = """        if(CopyBuffer(ribbon_hma10, 0, 0, 20, hma10_buf) < 20) { Print("DEBUG: ribbon10 fail"); return; } ArraySetAsSeries(hma10_buf, true);
        if(CopyBuffer(ribbon_hma21, 0, 0, 20, hma21_buf) < 20) { Print("DEBUG: ribbon21 fail"); return; } ArraySetAsSeries(hma21_buf, true);
        if(CopyBuffer(ribbon_hma50, 0, 0, 20, hma50_buf) < 20) { Print("DEBUG: ribbon50 fail"); return; } ArraySetAsSeries(hma50_buf, true);
        if(CopyBuffer(ribbon_hma100, 0, 0, 20, hma100_buf) < 20) { Print("DEBUG: ribbon100 fail"); return; } ArraySetAsSeries(hma100_buf, true);
        if(CopyBuffer(ribbon_hma200, 0, 0, 20, hma200_buf) < 20) { Print("DEBUG: ribbon200 fail"); return; } ArraySetAsSeries(hma200_buf, true);
        if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) { Print("DEBUG: rsi fail"); return; }
        if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) { Print("DEBUG: atr fail"); return; }
        if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) { Print("DEBUG: atr200 fail"); return; }
        if(CopyBuffer(atr_d1_handle,  0, 1, 1,  atr_d1_buf) < 1) { Print("DEBUG: atr_d1 fail"); return; }
        if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  { Print("DEBUG: sma20 fail"); return; }
        if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  { Print("DEBUG: stddev fail"); return; }"""

content = content.replace(target_multi, new_multi)

target_tf = """        if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;
        if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) return;
        
        int h4_shift = iBarShift(m_symbol, PERIOD_H4, currentBarTime);
        int d1_shift = iBarShift(m_symbol, PERIOD_D1, currentBarTime);
        int h1_shift = iBarShift(m_symbol, PERIOD_H1, currentBarTime);
        
        if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) return;
        if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) return;
        
        if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) return;"""

new_tf = """        if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) { Print("DEBUG: ema50 fail"); return; }
        if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) { Print("DEBUG: ema200 fail"); return; }
        
        int h4_shift = iBarShift(m_symbol, PERIOD_H4, currentBarTime);
        int d1_shift = iBarShift(m_symbol, PERIOD_D1, currentBarTime);
        int h1_shift = iBarShift(m_symbol, PERIOD_H1, currentBarTime);
        
        if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) { Print("DEBUG: ema20h4 fail"); return; }
        if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) { Print("DEBUG: ema50d1 fail"); return; }
        
        if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) { Print("DEBUG: adx fail"); return; }"""

content = content.replace(target_tf, new_tf)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Debug prints added to CopyBuffers.")
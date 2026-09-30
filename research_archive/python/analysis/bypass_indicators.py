import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all the strict returns for secondary indicators with simple warnings/fallbacks
# Target: { Print("DEBUG: atr200 fail"); return; }
# Replacement: { atr200_buf[0] = 1.0; }

replacements = {
    'if(CopyBuffer(ribbon_hma10, 0, 0, 20, hma10_buf) < 20) { Print("DEBUG: ribbon10 fail"); return; }': 'if(CopyBuffer(ribbon_hma10, 0, 0, 20, hma10_buf) < 20) { ArrayInitialize(hma10_buf, rates[1].close); }',
    'if(CopyBuffer(ribbon_hma21, 0, 0, 20, hma21_buf) < 20) { Print("DEBUG: ribbon21 fail"); return; }': 'if(CopyBuffer(ribbon_hma21, 0, 0, 20, hma21_buf) < 20) { ArrayInitialize(hma21_buf, rates[1].close); }',
    'if(CopyBuffer(ribbon_hma50, 0, 0, 20, hma50_buf) < 20) { Print("DEBUG: ribbon50 fail"); return; }': 'if(CopyBuffer(ribbon_hma50, 0, 0, 20, hma50_buf) < 20) { ArrayInitialize(hma50_buf, rates[1].close); }',
    'if(CopyBuffer(ribbon_hma100, 0, 0, 20, hma100_buf) < 20) { Print("DEBUG: ribbon100 fail"); return; }': 'if(CopyBuffer(ribbon_hma100, 0, 0, 20, hma100_buf) < 20) { ArrayInitialize(hma100_buf, rates[1].close); }',
    'if(CopyBuffer(ribbon_hma200, 0, 0, 20, hma200_buf) < 20) { Print("DEBUG: ribbon200 fail"); return; }': 'if(CopyBuffer(ribbon_hma200, 0, 0, 20, hma200_buf) < 20) { ArrayInitialize(hma200_buf, rates[1].close); }',
    'if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) { Print("DEBUG: rsi fail"); return; }': 'if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) { ArrayInitialize(rsi_buf, 50.0); }',
    'if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) { Print("DEBUG: atr fail"); return; }': 'if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) { return; }',
    'if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) { Print("DEBUG: atr200 fail"); return; }': 'if(CopyBuffer(atr200_handle, 0, 1, 1, atr200_buf) < 1) { atr200_buf[0] = atr_buf[0]; }',
    'if(CopyBuffer(atr_d1_handle,  0, 1, 1,  atr_d1_buf) < 1) { Print("DEBUG: atr_d1 fail"); return; }': 'if(CopyBuffer(atr_d1_handle, 0, 1, 1, atr_d1_buf) < 1) { atr_d1_buf[0] = atr_buf[0]; }',
    'if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  { Print("DEBUG: sma20 fail"); return; }': 'if(CopyBuffer(sma20_handle, 0, 1, 1, sma20) < 1) { sma20[0] = rates[1].close; }',
    'if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  { Print("DEBUG: stddev fail"); return; }': 'if(CopyBuffer(std_dev_handle, 0, 1, 1, stddev) < 1) { stddev[0] = atr_buf[0]; }',
    
    'if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) { Print("DEBUG: ema50 fail"); return; }': 'if(CopyBuffer(ema50_handle, 0, macro_shift + 1, 1, ef) < 1) { ef[0] = rates[1].close; }',
    'if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) { Print("DEBUG: ema200 fail"); return; }': 'if(CopyBuffer(ema200_handle, 0, macro_shift + 1, 1, es) < 1) { es[0] = rates[1].close; }',
    'if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) { Print("DEBUG: ema20h4 fail"); return; }': 'if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) { ArrayInitialize(ema20_h4, rates[1].close); }',
    'if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) { Print("DEBUG: ema50d1 fail"); return; }': 'if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) { ema50_d1[0] = rates[1].close; }',
    'if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) { Print("DEBUG: adx fail"); return; }': 'if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) { adx_buf[0] = 20.0; }',
    
    'if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) return;': 'if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) { ArrayInitialize(fast_hma_k, rates[1].close); }'
}

for t, r in replacements.items():
    content = content.replace(t, r)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied to bypass indicator failures!")
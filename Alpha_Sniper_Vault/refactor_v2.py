with open('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v4.mq5', 'r', encoding='utf-8') as f:
    c = f.read()

# Enable MetaLabeling & Zero Entry Threshold for Harvest
c = c.replace('InpMetaLabeling = false;', 'InpMetaLabeling = true;')
c = c.replace('InpEntryThreshold           = 0.50;', 'InpEntryThreshold           = 0.00;')

# --- THE FIX: We change the start_pos of the CopyBuffer instead of replacing [0] blindly ---

# 1. RSI
c = c.replace(
    'CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf)',
    'CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf)'
)

# 2. ATRs, SMA, STDDEV
c = c.replace(
    'CopyBuffer(atr_handle,     0, 0, 51, atr_buf)',
    'CopyBuffer(atr_handle,     0, 1, 51, atr_buf)'
)
c = c.replace(
    'CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf)',
    'CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf)'
)
c = c.replace(
    'CopyBuffer(atr_d1_handle,  0, 0, 1,  atr_d1_buf)',
    'CopyBuffer(atr_d1_handle,  0, 1, 1,  atr_d1_buf)'
)
c = c.replace(
    'CopyBuffer(sma20_handle,   0, 0, 1,  sma20)',
    'CopyBuffer(sma20_handle,   0, 1, 1,  sma20)'
)
c = c.replace(
    'CopyBuffer(std_dev_handle, 0, 0, 1,  stddev)',
    'CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)'
)

# 3. MACRO INDICATORS (Add +1 to shift)
c = c.replace(
    'CopyBuffer(ema50_handle,    0, macro_shift, 1, ef)',
    'CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)'
)
c = c.replace(
    'CopyBuffer(ema200_handle,   0, macro_shift, 1, es)',
    'CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)'
)
c = c.replace(
    'CopyBuffer(ema20_h4_handle, 0, h4_shift, 2, ema20_h4)',
    'CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4)'
)
c = c.replace(
    'CopyBuffer(ema50_d1_handle, 0, d1_shift, 1, ema50_d1)',
    'CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1)'
)
c = c.replace(
    'CopyBuffer(adx_handle, 0, h1_shift, 1, adx_buf)',
    'CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf)'
)

# 4. HMA Features (We manually adjust the HMA accesses inside ProcessTick, since hma_entry is copied at 0 for trigger logic)
# Note: hma_entry[0] is used in CalcBreakoutForceATR and hma_vel. We change them to [1].
parts = c.split('void ProcessTick()')
if len(parts) == 2:
    header = parts[0]
    body = parts[1]
    
    body = body.replace('hma_entry[2] - hma_entry[3]', 'hma_entry[3] - hma_entry[4]')
    body = body.replace('hma_entry[1] - hma_entry[2]', 'hma_entry[2] - hma_entry[3]')
    body = body.replace('hma_entry[0] - hma_entry[1]', 'hma_entry[1] - hma_entry[2]')
    body = body.replace('CalcBreakoutForceATR(current_close, hma_entry[0], current_atr)', 'CalcBreakoutForceATR(current_close, hma_entry[1], current_atr)')
    body = body.replace('MathAbs(rates[0].close - hma_entry[0])', 'MathAbs(rates[1].close - hma_entry[1])')
    
    # 5. Fix arrays from v4
    body = body.replace('double features[20];', 'double features[19];')
    body = body.replace('features[18] = feat_price_dev_atr;\n        features[19] = feat_opposite_bars;', 'features[18] = feat_opposite_bars;')
    body = body.replace('PriceDeviationATR,OppositeBarsCount', 'OppositeBarsCount')
    body = body.replace('feat_price_dev_atr, feat_opposite_bars', 'feat_opposite_bars')
    body = body.replace('%.5f,%.0f,%.5f,%d', '%.0f,%.5f,%d')

    c = header + 'void ProcessTick()' + body

with open('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v5.mq5', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done fixing CopyBuffers.')

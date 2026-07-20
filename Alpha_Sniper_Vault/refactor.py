import re

path = 'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v5.mq5'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Enable Meta Labeling
content = re.sub(r'InpMetaLabeling = false;', 'InpMetaLabeling = true;', content)
# Disable AI Filter for Harvest
content = re.sub(r'InpEntryThreshold\s*=\s*0\.50;', 'InpEntryThreshold           = 0.00;', content)

# Purge look-ahead bias from features
replacements = {
    'rsi_buf[0]': 'rsi_buf[1]',
    'sma20[0]': 'sma20[1]',
    'stddev[0]': 'stddev[1]',
    'ef[0]': 'ef[1]',
    'es[0]': 'es[1]',
    'ema20_h4[0]': 'ema20_h4[1]',
    'ema50_d1[0]': 'ema50_d1[1]',
    'atr_d1_buf[0]': 'atr_d1_buf[1]',
    'atr200_buf[0]': 'atr200_buf[1]',
    'adx_buf[0]': 'adx_buf[1]',
    'hma_entry[0] - hma_entry[1]': 'hma_entry[1] - hma_entry[2]',
    'hma_entry[1] - hma_entry[2]': 'hma_entry[2] - hma_entry[3]', # Shift vel_prev_k
    'hma_entry[2] - hma_entry[3]': 'hma_entry[3] - hma_entry[4]', # Shift vel_prev2_k
    'hma_entry[0]': 'hma_entry[1]',
}

# Apply replacements specifically inside ProcessTick to avoid messing up other things
# We'll split the file at ProcessTick
parts = content.split('void ProcessTick()')
if len(parts) == 2:
    header = parts[0]
    body = parts[1]
    
    # We must be careful about cascading replacements. 
    # For HMA differences, replace longer strings first.
    body = body.replace('hma_entry[2] - hma_entry[3]', 'hma_entry[3] - hma_entry[4]')
    body = body.replace('hma_entry[1] - hma_entry[2]', 'hma_entry[2] - hma_entry[3]')
    body = body.replace('hma_entry[0] - hma_entry[1]', 'hma_entry[1] - hma_entry[2]')
    
    body = body.replace('rsi_buf[0]', 'rsi_buf[1]')
    body = body.replace('sma20[0]', 'sma20[1]')
    body = body.replace('stddev[0]', 'stddev[1]')
    body = body.replace('ef[0]', 'ef[1]')
    body = body.replace('es[0]', 'es[1]')
    body = body.replace('ema20_h4[0]', 'ema20_h4[1]')
    body = body.replace('ema50_d1[0]', 'ema50_d1[1]')
    body = body.replace('atr_d1_buf[0]', 'atr_d1_buf[1]')
    body = body.replace('atr200_buf[0]', 'atr200_buf[1]')
    body = body.replace('adx_buf[0]', 'adx_buf[1]')
    body = body.replace('hma_entry[0]', 'hma_entry[1]')
    
    content = header + 'void ProcessTick()' + body

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Refactored MQL5 successfully.")

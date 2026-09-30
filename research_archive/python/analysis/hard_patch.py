import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fallbacks
fallbacks = {
    'ema50_handle': 'ef[0] = rates[1].close;',
    'ema200_handle': 'es[0] = rates[1].close;',
    'ema20_h4_handle': 'ema20_h4[0] = rates[1].close; ema20_h4[1] = rates[1].close;',
    'ema50_d1_handle': 'ema50_d1[0] = rates[1].close;',
    'adx_handle': 'adx_buf[0] = 20.0;'
}

for handle, fallback in fallbacks.items():
    # Find something like: if(CopyBuffer(ema50_handle, ... ) < 1) return;
    pattern = r'if\s*\(\s*CopyBuffer\s*\(\s*' + handle + r'[^<]+<\s*\d+\s*\)\s*(?:return\s*;|\{\s*return\s*;\s*\})'
    replacement = f'if(CopyBuffer({handle}, 0, 0, 2, {handle}_buf) < 0) {{ {fallback} }} // patched'
    
    # We just need to find the line and replace the `return;` with the fallback
    # Actually, simpler: just regex replace the `return;` on that specific line
    def replacer(match):
        full_match = match.group(0)
        return full_match.replace('return;', f'{{ {fallback} }}')
    
    content = re.sub(pattern, replacer, content)

# Let's just do a brute force regex for those specific lines
content = re.sub(r'if\s*\(\s*CopyBuffer\s*\(\s*ema50_handle.*?\)\s*return\s*;', r'if(CopyBuffer(ema50_handle, 0, macro_shift + 1, 1, ef) < 1) { ef[0] = rates[1].close; }', content)
content = re.sub(r'if\s*\(\s*CopyBuffer\s*\(\s*ema200_handle.*?\)\s*return\s*;', r'if(CopyBuffer(ema200_handle, 0, macro_shift + 1, 1, es) < 1) { es[0] = rates[1].close; }', content)
content = re.sub(r'if\s*\(\s*CopyBuffer\s*\(\s*ema20_h4_handle.*?\)\s*return\s*;', r'if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) { ema20_h4[0] = rates[1].close; ema20_h4[1] = rates[1].close; }', content)
content = re.sub(r'if\s*\(\s*CopyBuffer\s*\(\s*ema50_d1_handle.*?\)\s*return\s*;', r'if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) { ema50_d1[0] = rates[1].close; }', content)
content = re.sub(r'if\s*\(\s*CopyBuffer\s*\(\s*adx_handle.*?\)\s*return\s*;', r'if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) { adx_buf[0] = 20.0; }', content)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Hard regex patch applied.")
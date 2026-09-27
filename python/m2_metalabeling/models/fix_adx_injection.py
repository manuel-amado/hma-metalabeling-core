import re

files = [
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'
]

for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        code = f.read()

    # We need to inject `if(!IsRegimeTrending()) return;` 
    # right after `if (_sqIsBarOpen == true && LongEntrySignal && TradeLongs) {`
    
    code = re.sub(
        r'(if\s*\(_sqIsBarOpen\s*==\s*true\s*&&\s*LongEntrySignal\s*&&\s*TradeLongs\s*\)\s*\{)',
        r'\1\n        if(!IsRegimeTrending()) return;',
        code
    )

    code = re.sub(
        r'(if\s*\(_sqIsBarOpen\s*==\s*true\s*&&\s*\(ShortEntrySignal\s*&&\s*!LongEntrySignal\)\s*&&\s*TradeShorts\s*\)\s*\{)',
        r'\1\n        if(!IsRegimeTrending()) return;',
        code
    )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(code)

print('ADX filter correctly injected into both EAs.')

import re

files = [
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy_XAUUSD_Production.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\portfolio\XAUUSD\Strategy_XAUUSD_Production.mq5'
]

for p in files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            code = f.read()

        # Replace hardcoded SQX symbol strings with empty strings so correctSymbol() resolves to current chart
        code = re.sub(
            r'input\s+string\s+Subchart1Symbol\s*=\s*"[^"]*";',
            'input string Subchart1Symbol = "";',
            code
        )
        code = re.sub(
            r'input\s+string\s+Subchart2Symbol\s*=\s*"[^"]*";',
            'input string Subchart2Symbol = "";',
            code
        )

        with open(p, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"Patched: {p}")
    except Exception as e:
        print(f"Error patching {p}: {e}")

print('All EAs updated to auto-detect chart symbol.')

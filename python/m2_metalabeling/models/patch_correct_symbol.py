import re

files = [
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy_XAUUSD_Production.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5',
    r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\portfolio\XAUUSD\Strategy_XAUUSD_Production.mq5'
]

replacement = """string correctSymbol(string symbol){
    if(symbol == NULL || symbol == "NULL" || symbol == "Current" || symbol == "0" || symbol == "Same as main chart" || symbol == "" || StringFind(symbol, "_TICK_") >= 0) {
        return Symbol();
    }"""

for p in files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            code = f.read()

        # Patch the correctSymbol function
        code = re.sub(
            r'string\s+correctSymbol\s*\(\s*string\s+symbol\s*\)\s*\{\s*if\s*\(\s*symbol\s*==\s*NULL[^\{]*\{\s*return\s*Symbol\(\);\s*\}',
            replacement,
            code
        )

        with open(p, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"Patched correctSymbol in: {p}")
    except Exception as e:
        print(f"Error patching {p}: {e}")

print('All EAs updated to force-ignore legacy SQX symbols.')

import os
filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_V20_Extractor.mq5'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('handle_hma = iCustom(_Symbol, _Period, "Examples\\\\HMA", InpRefHMA_Period, 0, PRICE_CLOSE);', 'handle_hma = iCustom(_Symbol, _Period, "HMA50", InpRefHMA_Period);')

with open(filepath, 'w') as f:
    f.write(content)

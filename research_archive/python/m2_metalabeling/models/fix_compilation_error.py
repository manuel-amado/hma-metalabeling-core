import re
import os

f_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'
with open(f_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the undeclared 'trade' error by replacing it with the StrategyQuant wrapper OrderModify
code = code.replace(
    'trade.PositionModify(posTicket, new_sl, 0);',
    'OrderModify(posTicket, new_sl, 0);'
)

with open(f_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Extractor parcheado: Error de compilacion resuelto (reemplazado trade.PositionModify por OrderModify).")

import re
import os

symbols = ['XAUUSD', 'EURUSD', 'XAGUSD', 'GBPJPY', 'USDJPY', 'AUDUSD', 'AUDCAD']

# 1. Create XGBoost_Model_v12_*_M15.mqh
for sym in symbols:
    src_path = f'XGBoost_Model_{sym}_M15.mqh'
    dst_path = f'XGBoost_Model_v12_{sym}_M15.mqh'
    if os.path.exists(src_path):
        with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # Rename function name
        content = re.sub(rf'XGBoost_Predict_{sym}\b', f'XGBoost_Predict_v12_{sym}', content)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Created {dst_path}')
    else:
        print(f'WARNING: {src_path} not found')

# 2. Create Alpha_Sniper_v12.mq5 from Alpha_Sniper_v11_4.mq5
with open('Alpha_Sniper_v11_4.mq5', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# Update version
code = code.replace('#property version   "11.40"', '#property version   "12.00"')
code = code.replace('#property version   "11.30"', '#property version   "12.00"')

# Update includes
for sym in symbols:
    code = code.replace(f'#include "XGBoost_Model_{sym}_M15.mqh"', f'#include "XGBoost_Model_v12_{sym}_M15.mqh"')
    code = code.replace(f'XGBoost_Predict_{sym}(features)', f'XGBoost_Predict_v12_{sym}(features)')

# Update Dataset CSV name
code = code.replace('"Alpha_Sweep_Dataset_" + m_symbol + ".csv"', '"Alpha_Sweep_Dataset_v12_" + m_symbol + ".csv"')

# Update CSV Header
code = code.replace('VolSpreadRatio,Spread,TrigRejTail', 'VolSpreadRatio,SpreadATRRatio,TrigRejTail')

# Restore spread hard filter
code = re.sub(
    r'if\s*\(\s*false\s*\)\s*\{\s*Print\s*\(\s*"ABORT:\s*Spread demasiado alto',
    'if(spread > max_allowed_spread) {\n            Print("ABORT: Spread demasiado alto',
    code
)

# Normalize features[12]
target_feat = 'features[12] = spread;'
replacement_feat = '''double spread_atr_ratio = 0.0;
        if(current_atr > 0.0) {
            spread_atr_ratio = (spread * pip) / current_atr;
        }
        features[12] = spread_atr_ratio; // PROTOCOLO V12: Ratio adimensional Spread_en_Precio / ATR(15)'''

if target_feat in code:
    code = code.replace(target_feat, replacement_feat)
    print('Successfully replaced features[12] = spread with spread_atr_ratio')
else:
    print('WARNING: target_feat not found in code')

with open('Alpha_Sniper_v12.mq5', 'w', encoding='utf-8') as f:
    f.write(code)
print('Created Alpha_Sniper_v12.mq5')

import re

def parse_mqh(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract robust scaler equations
    eqs = re.findall(r'f\[(\d+)\] = \(features\[\1\] - \((.*?)\)\) / \((.*?)\);', content)
    for eq in eqs:
        idx, center, scale = eq
        print(f"f[{idx}] Center: {center} Scale: {scale}")

parse_mqh('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/XGBoost_Model_v12_XAUUSD_M15.mqh')

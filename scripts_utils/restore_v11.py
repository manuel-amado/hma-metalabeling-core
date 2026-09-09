import sys
import os
import subprocess

src_dir = 'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src'
out_dir = 'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5'

models = {
    'modelo_m15_universal.pkl': 'XGBoost_Model_XAUUSD_M15.mqh',
    'modelo_EURUSD_M15.pkl': 'XGBoost_Model_EURUSD_M15.mqh',
    'modelo_XAGUSD_M15.pkl': 'XGBoost_Model_XAGUSD_M15.mqh',
    'modelo_GBPJPY_M15.pkl': 'XGBoost_Model_GBPJPY_M15.mqh',
    'modelo_USDJPY_M15.pkl': 'XGBoost_Model_USDJPY_M15.mqh',
    'modelo_AUDUSD_M15.pkl': 'XGBoost_Model_AUDUSD_M15.mqh',
    'modelo_AUDCAD_M15.pkl': 'XGBoost_Model_AUDCAD_M15.mqh'
}

for pkl, mqh in models.items():
    pkl_path = os.path.join(src_dir, 'output', pkl)
    mqh_path = os.path.join(out_dir, mqh)
    
    if os.path.exists(pkl_path):
        print(f"Restoring {mqh} from {pkl}...")
        subprocess.run([sys.executable, os.path.join(src_dir, 'export_model_to_mqh.py'), '--model', pkl_path, '--output', mqh_path])
    else:
        print(f"Missing {pkl}")

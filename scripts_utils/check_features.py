import sys
sys.path.append('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src')
import pickle

try:
    with open('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src/output/modelo_m15_universal.pkl', 'rb') as f:
        scaler, model = pickle.load(f)
        print(f"modelo_m15_universal features: {model.n_features_in_}")
except Exception as e:
    print(f"Error 1: {e}")

try:
    with open('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src/output/modelo_m15_xauusd.pkl', 'rb') as f:
        artifact = pickle.load(f)
        if isinstance(artifact, dict):
            model = artifact['model']
        else:
            model = artifact[1]
        print(f"modelo_m15_xauusd features: {model.n_features_in_}")
except Exception as e:
    print(f"Error 2: {e}")

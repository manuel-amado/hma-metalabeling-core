import sys
sys.path.append('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src')
import joblib
import os

folder = 'C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/src/output'
for f_name in os.listdir(folder):
    if f_name.endswith('.pkl'):
        path = os.path.join(folder, f_name)
        try:
            artifact = joblib.load(path)
            model = artifact['model'] if isinstance(artifact, dict) else artifact[1]
            print(f"{f_name}: {model.n_features_in_} features")
        except Exception as e:
            print(f"{f_name}: Error {e}")

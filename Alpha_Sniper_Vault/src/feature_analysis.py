import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output'
SYMS = ['XAUUSD', 'EURUSD', 'USDJPY']

all_importances = pd.DataFrame()

for sym in SYMS:
    path = os.path.join(MODEL_DIR, f'modelo_v16_1_per_asset_{sym}.pkl')
    if not os.path.exists(path):
        continue
    
    art = joblib.load(path)
    model = art['model']
    features = art['features_activas']
    
    booster = model.get_booster()
    # 'gain' implies the relative contribution of the corresponding feature to the model
    gain = booster.get_score(importance_type='gain')
    
    # Map feature f0, f1... to names if necessary
    # Booster might use f0, f1... instead of names if df wasn't properly named
    named_gains = {}
    for k, v in gain.items():
        if k.startswith('f') and k[1:].isdigit():
            idx = int(k[1:])
            named_gains[features[idx]] = v
        else:
            named_gains[k] = v
            
    # Normalize to 100%
    total_gain = sum(named_gains.values())
    norm_gain = {k: (v/total_gain)*100 for k, v in named_gains.items()}
    
    df_imp = pd.DataFrame.from_dict(norm_gain, orient='index', columns=[sym])
    if all_importances.empty:
        all_importances = df_imp
    else:
        all_importances = all_importances.join(df_imp, how='outer')

all_importances = all_importances.fillna(0)
all_importances['Average'] = all_importances.mean(axis=1)
all_importances = all_importances.sort_values('Average', ascending=False)

print("\n=== TOP FEATURES (Average Gain %) ===")
print(all_importances.round(2).head(15))

print("\n=== BOTTOM FEATURES (Candidates for Removal) ===")
print(all_importances.round(2).tail(5))

import pandas as pd
import numpy as np
import joblib
import os
import json
import xgboost as xgb

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
OUT_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output"
sym = "XAUUSD"

data_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_{sym}.csv")
model_path = os.path.join(OUT_DIR, f"modelo_m15_{sym}.pkl")

df = pd.read_csv(data_path)
art = joblib.load(model_path)
model = art['model']
scaler = art['scaler']
features = art['features_activas']

booster = model.get_booster()
config = json.loads(booster.save_config())
try:
    base_score = float(config["learner"]["learner_model_param"]["base_score"])
except:
    base_score = 0.5
print("Base Score:", base_score)
import math
init_margin = -math.log(1.0/base_score - 1.0) if base_score != 0.5 else 0.0
print("Init Margin (sum):", init_margin)

X = df[features].head(5)
X_scaled = scaler.transform(X)
proba = model.predict_proba(X_scaled)[:, 1]

dtrain = xgb.DMatrix(X_scaled)
margin = booster.predict(dtrain, output_margin=True)

print("\nPredicciones (Primeras 5 filas):")
for i in range(5):
    print(f"Fila {i}: Proba={proba[i]:.6f}, Margin (Sum of trees)={margin[i]:.6f}")

print("\nValores crudos de la Fila 0:")
print(X.iloc[0].to_dict())
print("\nValores escalados de la Fila 0:")
print(X_scaled[0])

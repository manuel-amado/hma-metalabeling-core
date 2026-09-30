import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\train_v17.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Alpha_Sweep_Dataset_v16_1_", "Alpha_Sweep_Dataset_v17_STERILIZED_")
content = content.replace("modelo_v16_1_per_asset", "modelo_v17_per_asset")
content = content.replace("metricas_v16_1", "metricas_v17")

# We need to drop 'Time' column if it exists in the features
# Find the line: X = df.drop(columns=['Label', 'ReturnPct'])
content = content.replace(
    "X = df.drop(columns=['Label', 'ReturnPct'])",
    "X = df.drop(columns=['Label', 'ReturnPct', 'Time'], errors='ignore')"
)

# And drop the noisy features I recommended, to make V17 truly an upgrade.
content = content.replace(
    "X = df.drop(columns=['Label', 'ReturnPct', 'Time'], errors='ignore')",
    "X = df.drop(columns=['Label', 'ReturnPct', 'Time', 'DayOfWeek', 'Spread', 'Feature_VPivotMonotonic', 'RSI_Memory_State'], errors='ignore')"
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# Patch the exporter script too
exp_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\export_model_to_mqh_per_asset_v17.py'
with open(exp_path, 'r', encoding='utf-8') as f:
    exp_content = f.read()

exp_content = exp_content.replace("modelo_v16_1_per_asset", "modelo_v17_per_asset")
exp_content = exp_content.replace("XGBoost_Model_v16_", "XGBoost_Model_v17_")
exp_content = exp_content.replace("XGBoost_Predict_v16_", "XGBoost_Predict_v17_")
exp_content = exp_content.replace("XGBOOST_THRESHOLD_v16_", "XGBOOST_THRESHOLD_v17_")

with open(exp_path, 'w', encoding='utf-8') as f:
    f.write(exp_content)
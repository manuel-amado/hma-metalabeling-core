import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Revert prediction function calls back to v16 so the EA can compile NOW to extract data.
content = content.replace("XGBoost_Predict_v17_XAUUSD", "XGBoost_Predict_v16_XAUUSD")
content = content.replace("XGBoost_Predict_v17_EURUSD", "XGBoost_Predict_v16_EURUSD")
content = content.replace("XGBoost_Predict_v17_USDJPY", "XGBoost_Predict_v16_USDJPY")
content = content.replace("XGBoost_Predict_v17_AUDUSD", "XGBoost_Predict_v16_AUDUSD")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Reverted to v16 placeholders")
import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("XGBoost_Model_v16_XAUUSD_M15.mqh", "XGBoost_Model_v17_XAUUSD_M15.mqh")
content = content.replace("XGBoost_Model_v16_EURUSD_M15.mqh", "XGBoost_Model_v17_EURUSD_M15.mqh")
content = content.replace("XGBoost_Model_v16_USDJPY_M15.mqh", "XGBoost_Model_v17_USDJPY_M15.mqh")
content = content.replace("XGBoost_Model_v16_AUDUSD_M15.mqh", "XGBoost_Model_v17_AUDUSD_M15.mqh")

content = content.replace("XGBoost_Predict_v16_", "XGBoost_Predict_v17_")
content = content.replace("XGBOOST_THRESHOLD_XAUUSD", "XGBOOST_THRESHOLD_v17_XAUUSD")
content = content.replace("XGBOOST_THRESHOLD_EURUSD", "XGBOOST_THRESHOLD_v17_EURUSD")
content = content.replace("XGBOOST_THRESHOLD_USDJPY", "XGBOOST_THRESHOLD_v17_USDJPY")
content = content.replace("XGBOOST_THRESHOLD_AUDUSD", "XGBOOST_THRESHOLD_v17_AUDUSD")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v17.mq5 updated to use V17 models!")
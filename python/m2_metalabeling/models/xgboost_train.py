import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
import xgboost as xgb

# 1. Load the dataset
df = pd.read_csv("XGBoost_Dataset_Final.csv")

# 2. Define Features and Target
feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
X = df[feature_cols]
y = df['Target']
profits = df['Profit']

# 3. Train-Test Split (Chronological)
split_idx = int(len(df) * 0.7)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
profits_train, profits_test = profits.iloc[:split_idx], profits.iloc[split_idx:]

# 4. Train the XGBoost Classifier
model = xgb.XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss'
)
model.fit(X_train, y_train)

# 5. Predictions on Out-Of-Sample
y_prob = model.predict_proba(X_test)[:, 1]

# Lock Threshold at 0.36
threshold = 0.36
y_pred = (y_prob >= threshold).astype(int)

# 6. Evaluate Performance
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
auc = roc_auc_score(y_test, y_prob)

filtered_profits = np.where(y_pred == 1, profits_test, 0.0)
filtered_equity = pd.Series(filtered_profits).cumsum()
baseline_equity = profits_test.sum()
filtered_total = filtered_profits.sum()

print("--- Out-of-Sample Metrics (Threshold 0.36) ---")
print(f"ROC AUC:   {auc:.3f}")
print(f"Precision: {prec:.3f}")
print(f"Recall:    {rec:.3f}")
print(f"Baseline Net Profit (OOS): ${baseline_equity:.2f}")
print(f"Filtered Net Profit (OOS): ${filtered_total:.2f}")

importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)
print("\n--- Feature Importance ---")
print(importance.to_string(index=False))

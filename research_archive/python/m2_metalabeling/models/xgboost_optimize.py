import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, precision_recall_curve
import xgboost as xgb
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 1. Load the dataset
df = pd.read_csv("XGBoost_Dataset_Final.csv")

feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']
X = df[feature_cols]
y = df['Target']
profits = df['Profit']

split_idx = int(len(df) * 0.7)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
profits_train, profits_test = profits.iloc[:split_idx], profits.iloc[split_idx:]

model = xgb.XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss'
)
model.fit(X_train, y_train)

y_prob = model.predict_proba(X_test)[:, 1]
baseline_profit = profits_test.sum()

# Task 1: Optimize Threshold by EV (Max Net Profit)
thresholds_test = np.arange(0.30, 0.72, 0.02)
results = []
best_profit = -float('inf')
best_thresh_profit = 0.5

print(f"--- Threshold Optimization (EV) ---")
print(f"Baseline Profit (No Filter): ${baseline_profit:.2f}")

for t in thresholds_test:
    preds = (y_prob >= t).astype(int)
    filtered_profit = np.sum(np.where(preds == 1, profits_test, 0.0))
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    results.append((t, filtered_profit, prec, rec))
    print(f"Threshold: {t:.2f} | Profit: ${filtered_profit:7.2f} | Prec: {prec:.3f} | Rec: {rec:.3f}")
    
    if filtered_profit > best_profit:
        best_profit = filtered_profit
        best_thresh_profit = t

print(f"\nBest Threshold for Max Profit: {best_thresh_profit:.2f} (Profit: ${best_profit:.2f})")

# Task 2: Precision-Recall Curve & F-beta
precisions, recalls, pr_thresholds = precision_recall_curve(y_test, y_prob)

# Find max recall where precision >= 0.55
valid_idx = np.where(precisions[:-1] >= 0.55)[0]
if len(valid_idx) > 0:
    best_idx = valid_idx[np.argmax(recalls[valid_idx])]
    best_thresh_pr = pr_thresholds[best_idx]
    print(f"\n--- PR Curve Optimization ---")
    print(f"Threshold for Prec > 0.55 & Max Recall: {best_thresh_pr:.3f}")
    print(f"At this threshold: Precision = {precisions[best_idx]:.3f}, Recall = {recalls[best_idx]:.3f}")
else:
    print("\nNo threshold meets Precision >= 0.55.")

# Plot PR Curve
plt.figure(figsize=(8,6))
plt.plot(recalls, precisions, marker='.', label='XGBoost M2')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve (M2 Model)')
plt.axhline(y=0.55, color='r', linestyle='--', label='Min Precision (0.55)')
plt.legend()
plt.grid()
plt.savefig("MetaLabeling_PR_Curve.png")
print("\nSaved PR Curve to MetaLabeling_PR_Curve.png")

# Plot New Equity Curve with Best Threshold
preds_opt = (y_prob >= best_thresh_profit).astype(int)
filtered_equity_opt = pd.Series(np.where(preds_opt == 1, profits_test, 0.0)).cumsum()
baseline_equity = profits_test.cumsum()

plt.figure(figsize=(10,6))
plt.plot(baseline_equity.values, label="M1 (Baseline)", color="red", alpha=0.6)
plt.plot(filtered_equity_opt.values, label=f"M1+M2 (Threshold {best_thresh_profit:.2f})", color="green", linewidth=2)
plt.title(f"Meta-Labeling Equity Curve (Optimized Thresh {best_thresh_profit:.2f})")
plt.xlabel("Number of Trades (OOS)")
plt.ylabel("Profit ($)")
plt.legend()
plt.grid(True)
plt.savefig("MetaLabeling_Equity_Curve_Optimized.png")
print("Saved Optimized Equity Curve to MetaLabeling_Equity_Curve_Optimized.png")

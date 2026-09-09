import pandas as pd
import numpy as np
import xgboost as xgb
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score
import matplotlib.pyplot as plt

# 1. Parse HTML for Labels
HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")

trades_html = []
entry_time = None
for row in soup.find_all("tr"):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) >= 10:
        if "in" in cols:
            entry_time = cols[0]
        elif "out" in cols and entry_time is not None:
            profit = float(cols[10].replace(" ",""))
            swap = float(cols[9].replace(" ",""))
            trades_html.append({"Time_str": entry_time, "PnL": profit + swap})
            entry_time = None

df_labels = pd.DataFrame(trades_html)
df_labels["Time"] = pd.to_datetime(df_labels["Time_str"], format="%Y.%m.%d %H:%M:%S")

# 2. Parse CSV for Features
CSV_FILE = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Master6_Dataset.csv"
df_features = pd.read_csv(CSV_FILE)
df_features["Time"] = pd.to_datetime(df_features["Time"], format="%Y.%m.%d %H:%M:%S")

# 3. Merge
df = pd.merge_asof(df_features.sort_values("Time"), df_labels.sort_values("Time"), on="Time", direction="nearest", tolerance=pd.Timedelta(seconds=60))
df = df.dropna(subset=["PnL"])

# 4. Define Target (Meta-Label)
# 1 if trade was a Win (PnL > 0), 0 if Loss (PnL <= 0)
df["Target"] = (df["PnL"] > 0).astype(int)

# 5. Features
X = df.drop(columns=["Time", "Time_str", "PnL", "Target"])
y = df["Target"]

# 6. Train/Test Split (Chronological)
split_idx = int(len(df) * 0.70)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
df_test = df.iloc[split_idx:].copy()

# 7. XGBoost Model
model = xgb.XGBClassifier(
    n_estimators=150, 
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# 8. Predict Probabilities
y_prob = model.predict_proba(X_test)[:, 1]
df_test["Prob_Win"] = y_prob

# 9. Evaluate thresholds
print("=== META-LABELING RESULTS (OOS 30%) ===")
base_winrate = y_test.mean()
base_profit = df_test["PnL"].sum()
base_trades = len(df_test)

print(f"BASELINE: Trades={base_trades} | WinRate={base_winrate*100:.1f}% | Profit=${base_profit:,.0f}")

thresholds = [0.1, 0.2, 0.25, 0.3, 0.35, 0.4]
for t in thresholds:
    filtered_df = df_test[df_test["Prob_Win"] >= t]
    f_trades = len(filtered_df)
    if f_trades == 0: continue
    f_winrate = filtered_df["Target"].mean()
    f_profit = filtered_df["PnL"].sum()
    saved_losses = len(df_test[(df_test["Prob_Win"] < t) & (df_test["Target"] == 0)])
    missed_wins = len(df_test[(df_test["Prob_Win"] < t) & (df_test["Target"] == 1)])
    print(f"Threshold > {t:.2f} | Trades={f_trades} | WinRate={f_winrate*100:.1f}% | Profit=${f_profit:,.0f} | Blocked Losses={saved_losses} | Blocked Wins={missed_wins}")

# Output feature importance
impdf = pd.DataFrame({"Feature": X.columns, "Importance": model.feature_importances_}).sort_values("Importance", ascending=False)
print("\nFEATURE IMPORTANCE:")
print(impdf.to_string(index=False))

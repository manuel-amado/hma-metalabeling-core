import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import confusion_matrix

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237092.html"
CSV_FILE = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Master6_Dataset.csv"

df_csv = pd.read_csv(CSV_FILE)
df_csv["Time"] = pd.to_datetime(df_csv["Time"], format="%Y.%m.%d %H:%M:%S")

try:
    tables = pd.read_html(HTML_FILE, encoding="utf-16")
except:
    tables = pd.read_html(HTML_FILE, encoding="utf-8")

df_html = tables[1]
deals_start_idx = 0
for i, row in df_html.iterrows():
    if any(isinstance(x, str) and "Transacciones" in x for x in row):
        deals_start_idx = i + 2
        break

df_deals = df_html.iloc[deals_start_idx:].copy().reset_index(drop=True)
entry_times = []
profits = []
current_entry_time = None
for i, row in df_deals.iterrows():
    direction = str(row[4]).strip().lower()
    if direction == "in":
        current_entry_time = pd.to_datetime(str(row[0]), format="%Y.%m.%d %H:%M:%S")
    elif direction in ["out", "in/out"] and current_entry_time is not None:
        try:
            total_pnl = float(str(row[8]).replace(" ", "")) + float(str(row[9]).replace(" ", "")) + float(str(row[10]).replace(" ", ""))
            entry_times.append(current_entry_time)
            profits.append(total_pnl)
            current_entry_time = None
        except: pass

df_pnl = pd.DataFrame({"Time": entry_times, "PnL": profits})

df_csv = df_csv.sort_values("Time")
df_pnl = df_pnl.sort_values("Time")
df = pd.merge_asof(df_csv, df_pnl, on="Time", direction="nearest", tolerance=pd.Timedelta("5m"))
df = df.dropna(subset=["PnL"]).copy()

# TOP 25% OF WINNING TRADES (Super Wins)
threshold = np.percentile(df[df["PnL"] > 0]["PnL"], 75)
print(f"Umbral de SUPER-GANA (Top 25% de Ganadoras) definido en > ${threshold:.2f}")
df["FatTail"] = (df["PnL"] >= threshold).astype(int)

features = ["Signal", "RSI", "DistEMA_ATR", "Breakout_ATR", "Buildup", "Impulse_ATR", "LossStreak", "CandleSize_ATR", "DailyATR"]

split_idx = int(len(df) * 0.70)
train = df.iloc[:split_idx]
test = df.iloc[split_idx:]

X_train, y_train = train[features], train["FatTail"]
X_test, y_test = test[features], test["FatTail"]

print(f"\nEntrenando XGBoost (Train: {len(X_train)} | Test: {len(X_test)})...")
ratio = (len(y_train) - sum(y_train)) / sum(y_train) if sum(y_train) > 0 else 1
model = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.01, scale_pos_weight=ratio, random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)

print("\n--- RESULTADOS DEL ML EN OOS ---")
test_filtered = test.copy()
test_filtered["Pred"] = preds

profit_original = test["PnL"].sum()
pf_original = abs(test[test["PnL"]>0]["PnL"].sum() / test[test["PnL"]<0]["PnL"].sum()) if test[test["PnL"]<0]["PnL"].sum() != 0 else 0

profit_ml = test_filtered[test_filtered["Pred"] == 1]["PnL"].sum()
pf_ml = abs(test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]>0)]["PnL"].sum() / test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]<0)]["PnL"].sum()) if test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]<0)]["PnL"].sum() != 0 else 0

trades_original = len(test)
trades_ml = len(test_filtered[test_filtered["Pred"] == 1])

print(f"Estrategia Base (OOS): Beneficio: ${profit_original:.2f} | Profit Factor: {pf_original:.2f} | Trades: {trades_original}")
print(f"Estrategia con Fat-Tail ML (OOS): Beneficio: ${profit_ml:.2f} | Profit Factor: {pf_ml:.2f} | Trades: {trades_ml}")

print("\nMatriz de Confusión Fat-Tail:")
print(confusion_matrix(y_test, preds))

imp = pd.DataFrame({"Feature": features, "Importance": model.feature_importances_}).sort_values("Importance", ascending=False)
print("\nImportancia de Features:\n", imp.to_string(index=False))
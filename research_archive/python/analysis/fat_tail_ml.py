import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237092.html"
CSV_FILE = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Master6_Dataset.csv"

# 1. READ CSV
print("Leyendo CSV de Features...")
df_csv = pd.read_csv(CSV_FILE)
df_csv["Time"] = pd.to_datetime(df_csv["Time"], format="%Y.%m.%d %H:%M:%S")

# 2. READ HTML
print("Leyendo Reporte HTML...")
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
trades = []

# Extraer operaciones in/out
for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 10:
        t = [c.get_text(strip=True) for c in cols]
        if "out" in t or "in/out" in t:
            try:
                # El formato de MT5: t[0] es la fecha de salida, pero necesitamos buscar el 'in' correspondiente o usar el order ticket.
                # Simplificamos: El ticket de entrada a veces est en HTML.
                pass
            except: pass

# Mtodo alternativo ms preciso para extraer entradas y salidas:
# Buscamos todas las filas. Las filas de deals (Transacciones) tienen la fecha, Deal, Order, Symbol, Type, Direction, Volume, Price, etc.
deals = []
for row in soup.find_all("tr"):
    t = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(t) >= 10 and "." in t[0] and ":" in t[0]:
        deals.append(t)

df_deals = pd.DataFrame(deals)
# Simplificacin: asociaremos cada operacin basndonos en el orden o buscaremos las posiciones completas.
# En su lugar, buscaremos la seccin de "Órdenes" o "Transacciones".
# Lo ms fcil es buscar las seales in y emparejarlas con in/out o out.
entry_times = []
profits = []

current_entry = None
for d in deals:
    if "in" in d or "in/out" in d and len(d) > 8:
        # Check if it's an entry
        direction_idx = 0
        for i, val in enumerate(d):
            if val in ["in", "in/out"]:
                direction_idx = i
                break
        if direction_idx > 0:
            if d[direction_idx] == "in":
                current_entry = pd.to_datetime(d[0], format="%Y.%m.%d %H:%M:%S")
            elif d[direction_idx] in ["out", "in/out"]:
                # This is a close. Get Profit.
                try:
                    profit = float(d[-3].replace(" ","")) + float(d[-4].replace(" ","")) # PnL + Swap
                    if current_entry is not None:
                        entry_times.append(current_entry)
                        profits.append(profit)
                        current_entry = None
                except:
                    pass

df_pnl = pd.DataFrame({"Time": entry_times, "PnL": profits})

# 3. MERGE (Aproximacin por cercana de tiempo)
print(f"Mergeando {len(df_csv)} features con {len(df_pnl)} pnl records...")
df_csv = df_csv.sort_values("Time")
df_pnl = df_pnl.sort_values("Time")
df = pd.merge_asof(df_csv, df_pnl, on="Time", direction="nearest", tolerance=pd.Timedelta("15m"))
df = df.dropna(subset=["PnL"])

print(f"Dataset final: {len(df)} operaciones cruzadas con xito.")

# 4. DEFINIR EL TARGET FAT-TAIL
# Vamos a etiquetar como "1" a las operaciones que estn en el top 15% de rentabilidad.
threshold = np.percentile(df[df["PnL"] > 0]["PnL"], 75) # Top 25% de las ganadoras
print(f"Umbral de Fat-Tail definido en > ${threshold:.2f}")

df["FatTail"] = (df["PnL"] > threshold).astype(int)

# 5. MACHINE LEARNING (XGBOOST)
features = ["Signal", "RSI", "DistEMA_ATR", "Breakout_ATR", "Buildup", "Impulse_ATR", "LossStreak", "CandleSize_ATR", "DailyATR"]

# Split temporal (Train 2022-2024, Test 2025-2026)
train = df[df["Time"] < "2025-01-01"]
test = df[df["Time"] >= "2025-01-01"]

X_train, y_train = train[features], train["FatTail"]
X_test, y_test = test[features], test["FatTail"]

print(f"\nEntrenando XGBoost cazador de Fat-Tails (Train: {len(X_train)} | Test: {len(X_test)})...")
# Usamos scale_pos_weight para lidiar con el desbalanceo severo de clases (pocos Fat Tails)
ratio = (len(y_train) - sum(y_train)) / sum(y_train)
model = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, scale_pos_weight=ratio, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
probas = model.predict_proba(X_test)[:, 1]

# Evaluacin en el conjunto de Test (2025-2026 - El ao estancado)
print("\n--- RESULTADOS DEL ML EN OOS (2025-2026) ---")
test_filtered = test.copy()
test_filtered["Pred"] = preds

profit_original = test["PnL"].sum()
pf_original = abs(test[test["PnL"]>0]["PnL"].sum() / test[test["PnL"]<0]["PnL"].sum()) if test[test["PnL"]<0]["PnL"].sum() != 0 else 0

profit_ml = test_filtered[test_filtered["Pred"] == 1]["PnL"].sum()
pf_ml = abs(test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]>0)]["PnL"].sum() / test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]<0)]["PnL"].sum()) if test_filtered[(test_filtered["Pred"] == 1) & (test_filtered["PnL"]<0)]["PnL"].sum() != 0 else 0

trades_original = len(test)
trades_ml = len(test_filtered[test_filtered["Pred"] == 1])

print(f"Estrategia Base (2025-2026): Beneficio: ${profit_original:.2f} | Profit Factor: {pf_original:.2f} | Trades: {trades_original}")
print(f"Estrategia con Fat-Tail ML (2025-2026): Beneficio: ${profit_ml:.2f} | Profit Factor: {pf_ml:.2f} | Trades: {trades_ml}")

print("\nMatriz de Confusin Fat-Tail:")
print(confusion_matrix(y_test, preds))
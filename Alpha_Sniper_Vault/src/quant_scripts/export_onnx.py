import sys
import pandas as pd
import numpy as np
import xgboost as xgb
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType
import onnx

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

threshold = np.percentile(df["PnL"], 80)
df["Target"] = (df["PnL"] >= threshold).astype(int)

features = ["Signal", "RSI", "DistEMA_ATR", "Breakout_ATR", "Buildup", "Impulse_ATR", "LossStreak", "CandleSize_ATR", "DailyATR"]
X = df[features].values # NumPy array para no tener nombres de features custom
y = df["Target"].values

ratio = (len(y) - sum(y)) / sum(y) if sum(y) > 0 else 1
model = xgb.XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.01, scale_pos_weight=ratio, random_state=42)
model.fit(X, y)

initial_type = [('float_input', FloatTensorType([None, 9]))]
onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_type, target_opset=12)

ONNX_PATH = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\FatTail_Model.onnx"
onnx.save_model(onnx_model, ONNX_PATH)
print(f"Modelo guardado en {ONNX_PATH}")

for input in onnx_model.graph.input:
    print(f"Input: {input.name}, Type: {input.type.tensor_type.elem_type}, Shape: {[dim.dim_value for dim in input.type.tensor_type.shape.dim]}")
for output in onnx_model.graph.output:
    print(f"Output: {output.name}, Type: {output.type.tensor_type.elem_type}, Shape: {[dim.dim_value for dim in output.type.tensor_type.shape.dim]}")
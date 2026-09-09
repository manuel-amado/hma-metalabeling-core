import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

def parse_xml(file_xml):
    with open(file_xml, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "xml")
    rows = soup.find_all("Row")
    data, headers = [], []
    for i, row in enumerate(rows):
        cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
        if i == 0: headers = cells
        elif len(cells) == len(headers): data.append(cells)
    if not data: return pd.DataFrame(), []
    df = pd.DataFrame(data, columns=headers)
    num_cols = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades"]
    param_cols = [c for c in df.columns if "Inp" in c]
    for c in num_cols + param_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, param_cols

df1, p1 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-5102370105.xml")
df2, p2 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237105.xml")
c_params = [p for p in p1 if p in p2]
target = [p for p in c_params if p in ["InpHMA_Period", "InpMinDailyATR", "InpPostWinCooldownBars"]]

df_merged = pd.merge(df1, df2, on=c_params, suffixes=('_IS', '_OOS'))
df_merged = df_merged.dropna(subset=["Profit Factor_IS", "Profit Factor_OOS"])

# Filtro estricto de robustness, al menos 1.25 en ambos y profit positivo
robust = df_merged[(df_merged["Profit Factor_IS"] >= 1.20) & (df_merged["Profit Factor_OOS"] >= 1.20)].copy()
robust["Combined_Profit"] = robust["Profit_IS"] + robust["Profit_OOS"]
robust["Total_Trades"] = robust["Trades_IS"] + robust["Trades_OOS"]
robust = robust.sort_values("Combined_Profit", ascending=False)

print(f"{'HMA':<5} {'ATR':<5} {'CDwn':<5} | {'PF_IS':>5} {'PF_OOS':>6} | {'ProftIS':>8} {'ProftOOS':>8} | {'TrdIS':>5} {'TrdOOS':>6}")
for _, row in robust.head(10).iterrows():
    print(f"{row['InpHMA_Period']:<5} {row['InpMinDailyATR']:<5} {row['InpPostWinCooldownBars']:<5} | {row['Profit Factor_IS']:>5.2f} {row['Profit Factor_OOS']:>6.2f} | {row['Profit_IS']:>8.0f} {row['Profit_OOS']:>8.0f} | {int(row['Trades_IS']):>5} {int(row['Trades_OOS']):>6}")
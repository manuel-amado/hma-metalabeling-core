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

# FILTRAR OVERFIT: Exigir un mínimo de consistencia matemática en ambas ventanas
robust = df_merged[(df_merged["Profit Factor_IS"] >= 1.30) & (df_merged["Profit Factor_OOS"] >= 1.30)].copy()

robust["Combined_Profit"] = robust["Profit_IS"] + robust["Profit_OOS"]
robust["Total_Trades"] = robust["Trades_IS"] + robust["Trades_OOS"]
robust["Avg_PF"] = (robust["Profit Factor_IS"] + robust["Profit Factor_OOS"]) / 2

# Ordenar por el que tenga el mejor balance de profit y consistencia
robust = robust.sort_values(["Avg_PF", "Combined_Profit"], ascending=[False, False])

if len(robust) == 0:
    print("WARNING: No robust combinations found without overfit (PF < 1.30 in one of the periods).")
else:
    print("--- MOST ROBUST NON-OVERFIT COMBINATIONS (SP500) ---")
    header_params = " ".join([f"{p.replace('Inp',''):<18}" for p in target])
    print(f"{header_params} | PF_IS  PF_OOS | ProftIS ProftOOS | TrdIS TrdOOS")
    for _, row in robust.head(10).iterrows():
        p_str = " ".join([f"{str(row[p]):<18}" for p in target])
        print(f"{p_str} | {row['Profit Factor_IS']:>5.2f}  {row['Profit Factor_OOS']:>5.2f} | {row['Profit_IS']:>7.0f} {row['Profit_OOS']:>7.0f} | {int(row['Trades_IS']):>5} {int(row['Trades_OOS']):>6}")
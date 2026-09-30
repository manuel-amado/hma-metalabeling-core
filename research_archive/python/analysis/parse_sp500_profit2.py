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
    num_cols = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades","Expected Payoff"]
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
df_merged["Combined_Profit"] = df_merged["Profit_IS"] + df_merged["Profit_OOS"]
df_merged["Total_Trades"] = df_merged["Trades_IS"] + df_merged["Trades_OOS"]
df_merged = df_merged.sort_values("Combined_Profit", ascending=False)

print("Top 10 by COMBINED PROFIT:")
for rank, (_, row) in enumerate(df_merged.head(10).iterrows(), 1):
    p_str = " ".join([f"{str(row[p]):<10}" for p in target])
    print(f"{p_str} | PF_IS: {row['Profit Factor_IS']:.2f} PF_OOS: {row['Profit Factor_OOS']:.2f} | Profit: ${row['Combined_Profit']:,.0f} | Trades: {int(row['Total_Trades'])}")

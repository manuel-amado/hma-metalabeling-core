import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pandas as pd
from bs4 import BeautifulSoup
def parse_xml(file_xml):
    with open(file_xml, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "xml")
    data = []
    headers = []
    for i, row in enumerate(soup.find_all("Row")):
        cells = [c.get_text(strip=True) for c in row.find_all("Cell")]
        if i == 0: headers = cells
        elif len(cells) == len(headers): data.append(cells)
    if not data: return pd.DataFrame(), []
    df = pd.DataFrame(data, columns=headers)
    for c in ["Profit","Profit Factor","Trades"] + [c for c in df.columns if "Inp" in c]:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df1 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237093.xml")
df2 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-5102370102.xml")
df_merged = pd.merge(df1, df2, on=["InpHMA_Period", "InpMinDailyATR", "InpPostWinCooldownBars"], suffixes=('_IS', '_OOS'))
df_merged["Combined_Profit"] = df_merged["Profit_IS"] + df_merged["Profit_OOS"]
df_merged["Total_Trades"] = df_merged["Trades_IS"] + df_merged["Trades_OOS"]
df_merged = df_merged.sort_values("Combined_Profit", ascending=False)
print(df_merged[["InpHMA_Period", "InpMinDailyATR", "InpPostWinCooldownBars", "Profit Factor_IS", "Profit Factor_OOS", "Combined_Profit", "Total_Trades"]].head(15))
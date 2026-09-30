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
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data, columns=headers)
    num_cols = ["Profit","Profit Factor","Sharpe Ratio","Equity DD %","Trades","Expected Payoff"]
    param_cols = [c for c in df.columns if "Inp" in c]
    for c in num_cols + param_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, param_cols

df1, params1 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237096.xml")
df2, params2 = parse_xml(r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237097.xml")

# Assuming df1 is IS and df2 is OOS (or vice versa). We merge on parameters.
# The parameters present should be the same.
common_params = [p for p in params1 if p in params2]

df_merged = pd.merge(df1, df2, on=common_params, suffixes=('_IS', '_OOS'))
df_merged = df_merged.dropna(subset=["Profit Factor_IS", "Profit Factor_OOS"])

df_merged["Combined_Profit"] = df_merged["Profit_IS"] + df_merged["Profit_OOS"]
df_merged["Avg_PF"] = (df_merged["Profit Factor_IS"] + df_merged["Profit Factor_OOS"]) / 2

df_merged = df_merged.sort_values("Avg_PF", ascending=False)

print(f"{'--- FORWARD MATRIX (IS vs OOS) ---':^120}")
header = " ".join([f"{p.replace('Inp',''):<16}" for p in common_params]) + " | PF_IS  PF_OOS | ProftIS ProftOOS | TrdIS TrdOOS"
print(header)
print("-" * len(header))

for rank, (_, row) in enumerate(df_merged.head(15).iterrows(), 1):
    p_str = " ".join([f"{str(row[p]):<16}" for p in common_params])
    pf_is, pf_oos = row['Profit Factor_IS'], row['Profit Factor_OOS']
    pr_is, pr_oos = row['Profit_IS'], row['Profit_OOS']
    tr_is, tr_oos = int(row['Trades_IS']), int(row['Trades_OOS'])
    print(f"{p_str} | {pf_is:>5.2f}  {pf_oos:>5.2f} | {pr_is:>7.0f} {pr_oos:>7.0f} | {tr_is:>5} {tr_oos:>6}")

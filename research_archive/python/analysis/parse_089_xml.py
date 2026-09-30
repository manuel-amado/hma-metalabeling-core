from bs4 import BeautifulSoup
import pandas as pd

# ======== XML: Optimization ========
file_xml = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237089.xml"
with open(file_xml, 'r', encoding='utf-8', errors='replace') as f:
    soup = BeautifulSoup(f.read(), 'xml')

rows = soup.find_all('Row')
data, headers = [], []
for i, row in enumerate(rows):
    cells = [c.get_text(strip=True) for c in row.find_all('Cell')]
    if i == 0: headers = cells
    elif len(cells) == len(headers): data.append(cells)

df = pd.DataFrame(data, columns=headers)
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='ignore')

print("=== COLUMNAS XML ===")
print(list(df.columns))
print(f"Total pases: {len(df)}")
print()

# Sort by Profit Factor
pf_col = 'Profit Factor'
df[pf_col] = pd.to_numeric(df[pf_col], errors='coerce')
df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')
df['Sharpe Ratio'] = pd.to_numeric(df['Sharpe Ratio'], errors='coerce')
df['Equity DD %'] = pd.to_numeric(df['Equity DD %'], errors='coerce')
df['Trades'] = pd.to_numeric(df['Trades'], errors='coerce')

df_sorted = df.sort_values(pf_col, ascending=False)

baseline_pf = 1.384
baseline_profit = 191802.8

print("=== RANKING COMPLETO - MASTER4 ===")
print(f"{'#':<4} {'AccelBars':<12} {'UseAccel':<12} {'PF':>8} {'vsBASE':>8} {'Profit':>12} {'Sharpe':>8} {'DD%':>8} {'Trades':>8}")
print("-"*85)
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    accel_val = row.get('InpAccelBars', row.get('Accel', '?'))
    use_accel = row.get('InpUseAccelExit', '?')
    delta = row[pf_col] - baseline_pf
    flag = "GANA" if row[pf_col] > baseline_pf else "----"
    print(f"{rank:<4} {str(accel_val):<12} {str(use_accel):<12} {row[pf_col]:>8.4f} {delta:>+8.4f} {row['Profit']:>12,.0f} {row['Sharpe Ratio']:>8.3f} {row['Equity DD %']:>8.2f}% {int(row['Trades']):>8}  {flag}")
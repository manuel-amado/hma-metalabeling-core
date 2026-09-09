from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237088.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

soup = BeautifulSoup(content, 'xml')
rows = soup.find_all('Row')
data = []
headers = []
for i, row in enumerate(rows):
    cells = row.find_all('Cell')
    row_data = [cell.get_text(strip=True) for cell in cells]
    if i == 0:
        headers = row_data
    else:
        if len(row_data) == len(headers):
            data.append(row_data)

df = pd.DataFrame(data, columns=headers)
for col in ['Profit', 'Profit Factor', 'Sharpe Ratio', 'Equity DD %', 'Trades', 'InpHMA_Exit_Period', 'Expected Payoff', 'InpHMA_Period']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Solo los primeros 4 (HMA_Entry = 200) - los limpios
df_200 = df[df['InpHMA_Period'] == 200].sort_values('Profit Factor', ascending=False)

baseline_pf   = 1.384
baseline_profit = 191802.8

print("MASTER3 - HMA Entry=200 - Ranking por HMA Exit Period")
print("-" * 70)
for rank, (_, row) in enumerate(df_200.iterrows(), 1):
    delta_pf = row['Profit Factor'] - baseline_pf
    delta_profit = row['Profit'] - baseline_profit
    flag = "GANA" if row['Profit Factor'] > baseline_pf else "PIERDE"
    print(f"#{rank} HMA_Exit={int(row['InpHMA_Exit_Period']):>3} | PF={row['Profit Factor']:.4f} ({delta_pf:+.4f}) | Profit={row['Profit']:>10,.0f} ({delta_profit:>+10,.0f}) | Sharpe={row['Sharpe Ratio']:.3f} | DD={row['Equity DD %']:.2f}% | {flag}")

print()
print("BASELINE (Master Inicial, sin HMA de salida) -> PF=1.384 | Profit=191,802")
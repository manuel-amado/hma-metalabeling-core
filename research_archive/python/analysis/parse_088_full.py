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

# Cast numerics
for col in ['Profit', 'Profit Factor', 'Sharpe Ratio', 'Equity DD %', 'Trades', 'InpHMA_Exit_Period', 'Expected Payoff', 'Recovery Factor']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_sorted = df.sort_values('Profit Factor', ascending=False)

print("=" * 80)
print("RANKING COMPLETO - MASTER3 - Optimizacion HMA Exit Period")
print("=" * 80)
print(f"{'Rank':<5} {'HMA_Exit':<10} {'Profit':>12} {'PF':>8} {'Sharpe':>8} {'DD%':>8} {'Trades':>8} {'Payoff':>10}")
print("-" * 80)
for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
    print(f"{rank:<5} {int(row['InpHMA_Exit_Period']):<10} {row['Profit']:>12,.2f} {row['Profit Factor']:>8.4f} {row['Sharpe Ratio']:>8.3f} {row['Equity DD %']:>8.2f}% {int(row['Trades']):>8} {row['Expected Payoff']:>10.2f}")

print()
print("=" * 80)
print("ANALISIS DE INFLEXION: Rendimiento por periodo de salida")
print("=" * 80)
baseline_pf = 1.384  # Referencia Master Base (IS)
baseline_profit = 191802.8

df_sorted_exit = df.sort_values('InpHMA_Exit_Period')
for _, row in df_sorted_exit.iterrows():
    delta_pf = row['Profit Factor'] - baseline_pf
    delta_profit = row['Profit'] - baseline_profit
    flag = "🏆" if row['Profit Factor'] > baseline_pf else "❌"
    print(f"HMA Exit {int(row['InpHMA_Exit_Period']):>3} | PF: {row['Profit Factor']:.4f} ({delta_pf:+.4f}) | Profit: {row['Profit']:>10,.0f} ({delta_profit:+,.0f}) | Sharpe: {row['Sharpe Ratio']:.3f} | DD: {row['Equity DD %']:.2f}% {flag}")
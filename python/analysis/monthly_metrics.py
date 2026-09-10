import pandas as pd
import numpy as np
import calendar

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

parsed = []
for line in html.split('\n'):
    if '>out<' in line:
        tds = line.split('<td')
        if len(tds) >= 12:
            try:
                time_str = tds[1].split('>')[1].split('<')[0].replace('.', '-')
                profit = float(tds[11].split('>')[1].split('<')[0].replace(' ', ''))
                parsed.append({'Time': pd.to_datetime(time_str), 'Profit': profit})
            except: pass

df = pd.DataFrame(parsed).sort_values('Time').reset_index(drop=True)
df['Year'] = df['Time'].dt.year
df['Month'] = df['Time'].dt.month

monthly = df.groupby(['Year', 'Month'])['Profit'].sum().reset_index()

total_months = len(monthly)
positive_months = len(monthly[monthly['Profit'] > 0])
negative_months = len(monthly[monthly['Profit'] <= 0])
win_rate_months = (positive_months / total_months) * 100

avg_monthly = monthly['Profit'].mean()
max_monthly = monthly['Profit'].max()
min_monthly = monthly['Profit'].min()

print(f"Total Meses Operados: {total_months}")
print(f"Meses Positivos: {positive_months} ({win_rate_months:.1f}%)")
print(f"Meses Negativos: {negative_months} ({(negative_months/total_months)*100:.1f}%)")
print(f"Promedio Mensual: ${avg_monthly:,.2f}")
print(f"Mejor Mes: ${max_monthly:,.2f}")
print(f"Peor Mes: ${min_monthly:,.2f}")
print("-" * 50)

# Pivot Table for Year/Month
pivot = monthly.pivot(index='Year', columns='Month', values='Profit').fillna(0)
# Translate month numbers to abbreviations
month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# Formatting pivot
header = "| Año | " + " | ".join(month_names) + " |"
separator = "|---|" + "|".join(["---"] * 12) + "|"
print(header)
print(separator)

for year in pivot.index:
    row_str = f"| **{year}** | "
    row_vals = []
    for m in range(1, 13):
        if m in pivot.columns:
            val = pivot.loc[year, m]
            if val == 0 and (year == 2026 and m > 8):
                row_vals.append("-")
            else:
                if val > 0:
                    row_vals.append(f"<span style='color:green'>+${val/1000:.1f}k</span>")
                elif val < 0:
                    row_vals.append(f"<span style='color:red'>-${abs(val)/1000:.1f}k</span>")
                else:
                    row_vals.append("$0")
        else:
            row_vals.append("-")
    row_str += " | ".join(row_vals) + " |"
    print(row_str)

import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237085.html'
with open(filepath, 'r', encoding='utf-16') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

metrics = {}
tables = soup.find_all('table')

for table in tables:
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            key = cells[0].text.strip().replace(':', '')
            val = cells[1].text.strip()
            metrics[key] = val
            if len(cells) >= 4:
                key2 = cells[2].text.strip().replace(':', '')
                val2 = cells[3].text.strip()
                metrics[key2] = val2

print("=== METRICS ===")
for k in ["Símbolo", "Período", "Beneficio neto total", "Factor de beneficio", "Beneficio esperado", "Transacciones totales", "Transacciones rentables (% del total)", "Drawdown del balance absoluto"]:
    print(f"{k}: {metrics.get(k, 'N/A')}")
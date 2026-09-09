import pandas as pd
import re
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
            key = cells[0].text.strip()
            val = cells[1].text.strip()
            metrics[key] = val
            if len(cells) >= 4:
                key2 = cells[2].text.strip()
                val2 = cells[3].text.strip()
                metrics[key2] = val2

print("=== KEY METRICS ===")
keys_to_print = ['Symbol', 'Period', 'Total net profit', 'Profit factor', 'Recovery factor', 'Expected payoff', 'Total trades', 'Profit trades (% of total)']
for k, v in metrics.items():
    if k in keys_to_print or k.startswith('Total net profit') or k.startswith('Profit factor'):
        print(f"{k}: {v}")
        
try:
    print(f"Total net profit: {metrics.get('Total net profit', 'N/A')}")
    print(f"Total trades: {metrics.get('Total trades', 'N/A')}")
    print(f"Profit factor: {metrics.get('Profit factor', 'N/A')}")
    print(f"Win rate: {metrics.get('Profit trades (% of total)', 'N/A')}")
except Exception as e:
    pass

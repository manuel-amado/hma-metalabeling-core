import pandas as pd
from bs4 import BeautifulSoup
import re

html_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237086.html"
with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=== METRICAS CLAVE ===")
tables = soup.find_all('table')
for t in tables:
    text = t.get_text(separator=' | ')
    if 'Beneficio Neto' in text or 'Factor de Beneficio' in text:
        rows = t.find_all('tr')
        for r in rows:
            print(r.get_text(separator=' : ').strip())

print("\n=== MAE / MFE y TIEMPO DE RETENCION ===")
# MFE/MAE usually in the same table
for t in tables:
    text = t.get_text()
    if 'MFE' in text or 'MAE' in text or 'retención' in text:
        rows = t.find_all('tr')
        for r in rows:
            clean_r = r.get_text(separator=' : ').strip()
            if 'MFE' in clean_r or 'MAE' in clean_r or 'retenci' in clean_r:
                print(clean_r)

print("\n=== BENEFICIOS POR HORA (Horarios Rentables) ===")
# Try to extract the hour table or look for hour-based strings
# MT5 sometimes creates javascript charts for this, or it might be in a table.
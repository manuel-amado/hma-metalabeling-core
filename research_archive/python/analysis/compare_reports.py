import os
from bs4 import BeautifulSoup
import re

files = [
    r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237093.html",
    r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237094.html",
    r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237097.html"
]

for f in files:
    print(f"\n--- Analizando: {os.path.basename(f)} ---")
    if not os.path.exists(f):
        print("Archivo no encontrado.")
        continue
        
    with open(f, 'r', encoding='utf-16', errors='replace') as file:
        content = file.read()
        if '<html' not in content.lower():
            with open(f, 'r', encoding='utf-8', errors='replace') as file2:
                content = file2.read()
                
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract key metrics
    text = soup.get_text()
    
    net_profit = re.search(r'Beneficio Neto[:\s]+([-\d\s\.]+)', text)
    pf = re.search(r'Factor de Beneficio[:\s]+([\d\.]+)', text)
    trades = re.search(r'Total de transacciones[:\s]+(\d+)', text)
    dd = re.search(r'Reducci.n relativa de la equidad[:\s]+([\d\.]+)%', text)
    
    print(f"Beneficio Neto: {net_profit.group(1).strip() if net_profit else 'N/A'}")
    print(f"Profit Factor: {pf.group(1).strip() if pf else 'N/A'}")
    print(f"Trades: {trades.group(1).strip() if trades else 'N/A'}")
    print(f"Drawdown (Eq): {dd.group(1).strip() if dd else 'N/A'}%")
    
    # Try to find input parameters table
    tables = soup.find_all('table')
    for table in tables:
        if 'InpUseAI' in table.get_text() or 'InpMaxImpulseATR' in table.get_text():
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    param_name = cols[0].get_text(strip=True)
                    if param_name in ['InpUseAI', 'InpMaxImpulseATR', 'InpMinDailyATR', 'InpATRMultiplier']:
                        param_val = cols[1].get_text(strip=True)
                        print(f"  {param_name} = {param_val}")
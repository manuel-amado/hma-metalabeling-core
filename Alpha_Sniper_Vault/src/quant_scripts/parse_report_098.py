from bs4 import BeautifulSoup
import re

f = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237098.html"
with open(f, 'r', encoding='utf-16', errors='replace') as file:
    content = file.read()
    if '<html' not in content.lower():
        with open(f, 'r', encoding='utf-8', errors='replace') as file2:
            content = file2.read()
            
soup = BeautifulSoup(content, 'html.parser')
text = soup.get_text()

net_profit = re.search(r'Beneficio Neto[:\s]+([-\d\s\.]+)', text)
pf = re.search(r'Factor de Beneficio[:\s]+([\d\.]+)', text)
trades = re.search(r'Total de transacciones[:\s]+(\d+)', text)
dd = re.search(r'Reducci.n relativa de la equidad[:\s]+([\d\.]+)%', text)
period = re.search(r'Periodo[:\s]+([^\n]+)', text)

print(f"Periodo: {period.group(1).strip() if period else 'N/A'}")
print(f"Beneficio Neto: {net_profit.group(1).strip() if net_profit else 'N/A'}")
print(f"Profit Factor: {pf.group(1).strip() if pf else 'N/A'}")
print(f"Trades: {trades.group(1).strip() if trades else 'N/A'}")
print(f"Drawdown (Eq): {dd.group(1).strip() if dd else 'N/A'}%")
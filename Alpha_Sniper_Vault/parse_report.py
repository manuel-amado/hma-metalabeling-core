import re

html = open(r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513697584.html', encoding='utf-16', errors='ignore').read()

labels = [
    'Beneficio neto total',
    'Beneficio bruto',
    'Pérdida bruta',
    'Factor de beneficio',
    'Beneficio esperado',
    'Reducción máxima de la equidad',
    'Transacciones totales',
    'Transacciones rentables',
    'Transacciones no rentables',
    'Promedio beneficio rentable',
    'Promedio pérdida no rentable'
]

data = {}
for l in labels:
    # Some MT5 reports put the value directly in the td, some in <b>
    m = re.search(r'>\s*' + l + r'.*?<td[^>]*>(?:.*?<b[^>]*>)?(.*?)(?:</b>)?</td>', html, re.I|re.S)
    if m:
        # Strip HTML tags just in case
        clean_val = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        data[l] = clean_val
    else:
        data[l] = None

for k, v in data.items():
    print(f"{k}: {v}")

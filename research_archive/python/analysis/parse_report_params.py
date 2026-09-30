import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import re

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237091.html"

try:
    with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
        content = fh.read()
except:
    try:
        with open(HTML_FILE, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except Exception as e:
        print(f"Error opening file: {e}")
        sys.exit(1)

soup = BeautifulSoup(content, "html.parser")
print("--- PARAMETROS EXTRAIDOS DEL REPORTE ---")

# En los reportes de MT5 HTML, a menudo hay un div o tr con el texto 'Parameters' o simplemente una lista en el div the_header
# Buscamos cualquier td o texto que contenga 'Inp' o similar.

params_found = []
for div in soup.find_all("div"):
    text = div.get_text()
    if "InpMagicNumber" in text or "InpHMA_Period" in text:
        # Intenta parsear el bloque de parametros
        parts = text.split(',')
        for p in parts:
            if "=" in p:
                params_found.append(p.strip())

if not params_found:
    # Buscar en tablas
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True)
            if "Inp" in key:
                val = cells[1].get_text(strip=True)
                params_found.append(f"{key}={val}")

if not params_found:
    # Búsqueda por Regex bruta
    matches = re.findall(r'([a-zA-Z0-9_]+=[a-zA-Z0-9_\.\-]+)', content)
    for m in matches:
        if "Inp" in m:
            params_found.append(m)

# Eliminar duplicados manteniendo orden
seen = set()
for p in params_found:
    if p not in seen:
        print(p)
        seen.add(p)

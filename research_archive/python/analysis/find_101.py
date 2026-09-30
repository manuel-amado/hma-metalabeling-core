import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import os, glob

# Buscar el archivo correcto
base = r"C:\Users\Manuel\Documents\BACKTESTS"
found = None
for root, dirs, files in os.walk(base):
    for f in files:
        if "101" in f and f.endswith(".html"):
            found = os.path.join(root, f)
            break

if not found:
    # Intentar el path directo con nombre completo
    candidates = glob.glob(r"C:\Users\Manuel\Documents\BACKTESTS\**\*101*.html", recursive=True)
    if candidates:
        found = candidates[0]

print(f"Archivo encontrado: {found}")

# Leer con todas las codificaciones posibles
content = None
if found:
    for enc in ["utf-16","utf-16-le","utf-16-be","utf-8","latin-1","cp1252"]:
        try:
            with open(found, "r", encoding=enc, errors="replace") as fh:
                tmp = fh.read()
            if len(tmp) > 1000 and ("<html" in tmp.lower() or "<table" in tmp.lower()):
                content = tmp
                print(f"Leido con encoding: {enc}, chars: {len(tmp)}")
                break
        except Exception as e:
            print(f"Fallo {enc}: {e}")

if not content:
    # Intentar leer binario y detectar BOM
    with open(found, "rb") as fh:
        raw = fh.read()
    print(f"BOM bytes: {raw[:4].hex()}")
    # UTF-16 BOM: ff fe o fe ff
    if raw[:2] == b'\xff\xfe':
        content = raw.decode("utf-16-le", errors="replace")
    elif raw[:2] == b'\xfe\xff':
        content = raw.decode("utf-16-be", errors="replace")
    else:
        content = raw.decode("utf-8", errors="replace")

soup = BeautifulSoup(content, "html.parser")
trades = []
for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 10:
        t = [c.get_text(strip=True) for c in cols]
        if "out" in t:
            try:
                trades.append((t[0], float(t[-3].replace(" ","")), float(t[-4].replace(" ",""))))
            except: pass

print(f"Trades parseados: {len(trades)}")
if len(trades) < 5:
    # Mostrar primeras filas para debug
    for row in soup.find_all("tr")[:10]:
        print([c.get_text(strip=True) for c in row.find_all("td")])
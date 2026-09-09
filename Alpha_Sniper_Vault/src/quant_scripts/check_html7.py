from bs4 import BeautifulSoup
HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370100.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
for row in soup.find_all("tr"):
    text = row.get_text(strip=True)
    if "Beneficio Neto" in text or "Factor de Beneficio" in text or "Total de operaciones" in text or "Ratio de Sharpe" in text or "Reducci" in text:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        print(cols)
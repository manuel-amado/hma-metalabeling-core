from bs4 import BeautifulSoup
HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
rows = soup.find_all("tr")
for i, row in enumerate(rows[50:100]):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if cols:
        print(i, cols)
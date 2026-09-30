from bs4 import BeautifulSoup

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")

deals = []
for row in soup.find_all("tr"):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) >= 10 and ("in" in cols or "out" in cols):
        deals.append(cols)
        if len(deals) >= 4:
            break

for d in deals:
    print(d)
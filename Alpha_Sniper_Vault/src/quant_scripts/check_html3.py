from bs4 import BeautifulSoup

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")

for row in soup.find_all("tr"):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) >= 10 and "out" in cols:
        print(cols)
        break
    elif len(cols) >= 10 and "in" in cols:
        print(cols)
        break
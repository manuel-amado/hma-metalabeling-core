from bs4 import BeautifulSoup

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370100.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
rows = soup.find_all("tr")

for i, row in enumerate(rows[:20]):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) > 1:
        print(cols)
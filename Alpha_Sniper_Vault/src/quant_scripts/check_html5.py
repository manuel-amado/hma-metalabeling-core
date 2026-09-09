from bs4 import BeautifulSoup

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370100.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
rows = soup.find_all("tr")

metrics = {}
for i, row in enumerate(rows[:20]):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) >= 2:
        metrics[cols[0]] = cols[1]
        if len(cols) >= 4:
            metrics[cols[2]] = cols[3]
        if len(cols) >= 6:
            metrics[cols[4]] = cols[5]

print("=== NEW BACKTEST RESULTS ===")
print("Trades:", metrics.get("Total de operaciones ejecutadas:", "N/A"))
print("Net Profit:", metrics.get("Beneficio Neto:", "N/A"))
print("Profit Factor:", metrics.get("Factor de Beneficio:", "N/A"))
print("Max DD (Equity):", metrics.get("Reduccin mxima de la equidad:", "N/A"))
print("Sharpe Ratio:", metrics.get("Ratio de Sharpe:", "N/A"))
print("Win Rate (L/S):", metrics.get("Posiciones largas (% rentables):", "N/A"), "/", metrics.get("Posiciones cortas (% rentables):", "N/A"))
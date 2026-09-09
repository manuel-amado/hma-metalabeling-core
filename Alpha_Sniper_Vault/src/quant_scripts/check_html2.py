from bs4 import BeautifulSoup
import pandas as pd

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237099.html"
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")

trades = []
for row in soup.find_all("tr"):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if len(cols) >= 10:
        if "out" in cols or "in/out" in cols:
            # Typical Deal row: Time | Deal | Symbol | Type | Direction(in/out) | Volume | Price | Order | Commission | Swap | Profit
            pass
        elif len(cols) == 13 and "." in cols[0] and ":" in cols[0]:
            # Typical Positions row: Time | Position | Symbol | Type | Volume | Price | S/L | T/P | Time | Price | Comm | Swap | Profit
            try:
                entry_time = cols[0]
                profit = float(cols[-1].replace(" ",""))
                swap = float(cols[-2].replace(" ",""))
                pnl = profit + swap
                trades.append((entry_time, pnl))
            except:
                pass

print(f"Found {len(trades)} trades in Positions table.")
if trades:
    print("First 5 trades:", trades[:5])
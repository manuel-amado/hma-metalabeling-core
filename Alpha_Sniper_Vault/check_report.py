import re

path = "C:/Users/Manuel/Documents/BACKTESTS/ReportTester-1513697586.html"
with open(path, "r", encoding="utf-16") as f:
    html = f.read()

text = re.sub(r'<[^>]+>', '|', html)
lines = [l.strip() for l in text.split('|') if l.strip()]

for i, l in enumerate(lines[:100]):
    print(f"{i}: {l}")

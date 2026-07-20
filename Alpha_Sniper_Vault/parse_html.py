path = 'C:/Users/Manuel/Documents/BACKTESTS/ReportTester-1513859263.html'
try:
    with open(path, 'r', encoding='utf-16') as f:
        html = f.read()
except:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

import re
text = re.sub(r'<[^>]+>', '\n', html)
lines = [line.strip() for line in text.split('\n') if line.strip()]

for i, line in enumerate(lines[100:150]):
    print(f"{i+100}: {line}")

import sys
import re

file_path = sys.argv[1]
try:
    with open(file_path, 'r', encoding='utf-16') as f:
        content = f.read()
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

# MT5 reports have <td>Title</td><td>Value</td>
metrics = [
    "Initial deposit", "Total net profit", "Gross profit", "Gross loss",
    "Profit factor", "Expected payoff", "Absolute drawdown", "Maximal drawdown",
    "Relative drawdown", "Total trades", "Short trades (won %)", "Long trades (won %)"
]

print("=== BACKTEST SUMMARY ===")
for metric in metrics:
    pattern = r'<td[^>]*>' + re.escape(metric) + r'</td>\s*<td[^>]*>(.*?)</td>'
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        val = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        print(f"{metric}: {val}")
    else:
        # try without exact case
        pass

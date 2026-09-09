import pandas as pd
from bs4 import BeautifulSoup
import re

html_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237086.html"
with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# Look for patterns that match hours and profits
# Usually MT5 HTML has a javascript array like:
# var chart_data = [...];
print("Searching for JS data or tables...")
js_blocks = re.findall(r'<script.*?>.*?</script>', html, re.DOTALL)
for js in js_blocks:
    if 'hour' in js.lower() or 'time' in js.lower() or 'series' in js.lower():
        # Look for data arrays
        data_arrays = re.findall(r'\[\[.*?\]\]', js)
        if data_arrays:
            print("Found JS Data Array (possible chart data):")
            for arr in data_arrays[:3]:
                print(arr[:100] + "...")
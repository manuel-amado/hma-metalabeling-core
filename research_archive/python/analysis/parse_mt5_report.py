import re
from bs4 import BeautifulSoup
import pandas as pd

try:
    with open(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237075.html", 'r', encoding='utf-16le') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    trades = []
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 8:
            text_vals = [td.get_text(strip=True) for td in tds]
            trades.append(text_vals)
                
    print(f"Found {len(trades)} potential rows.")
    if trades:
        for i in range(10, 20):
            print("Row", i, trades[i])
except Exception as e:
    print("Error:", e)

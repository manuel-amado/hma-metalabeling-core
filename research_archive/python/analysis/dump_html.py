import sys
from bs4 import BeautifulSoup
filepath = sys.argv[1]
with open(filepath, 'r', encoding='utf-16') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
for tr in soup.find_all('tr'):
    row_text = [td.get_text(strip=True) for td in tr.find_all('td')]
    if row_text:
        print(" | ".join(row_text))
import urllib.request
import re
from bs4 import BeautifulSoup

url = "https://www.fxstreet.es/calendario-economico"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
for s in soup.find_all('script'):
    src = s.get('src')
    if src:
        print("SCRIPT SRC:", src)
    else:
        text = s.string or ""
        if 'api' in text.lower() or 'calendar' in text.lower() or 'url' in text.lower() or 'token' in text.lower():
            print("SCRIPT INLINE (snippet):", text[:200])

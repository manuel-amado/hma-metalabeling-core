import urllib.request
import re

url = "https://staticcontent.fxsstatic.com/site/es/219229/_next/static/chunks/app/(calendar)/calendario-economico/page-ee85cab6b0899dda.js"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
js = urllib.request.urlopen(req).read().decode('utf-8')

for word in ["export", "csv", "event", "calendar", "acuity", "url", "api"]:
    matches = re.findall(rf'[^;]{{0,50}}{word}[^;]{{0,50}}', js, re.IGNORECASE)
    print(f"=== {word} (count: {len(matches)}) ===")
    for m in matches[:5]:
        print("  ->", m.strip())

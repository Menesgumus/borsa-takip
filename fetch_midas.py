import urllib.request
import re
import json

req = urllib.request.Request('https://www.getmidas.com/canli-borsa/bist-100-xu100/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    matches = re.findall(r'href="https://www\.getmidas\.com/canli-borsa/([^/]+)-hissesi/"', html)
    symbols = set([m.upper() for m in matches if len(m) <= 5])
    print(f"Midas symbols ({len(symbols)}):", list(symbols)[:10])
    with open("midas_symbols.json", "w") as f:
        json.dump(list(symbols), f)
except Exception as e:
    print(e)

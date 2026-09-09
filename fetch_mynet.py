import urllib.request
import re
import json
import ssl

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request('https://finans.mynet.com/borsa/endeks/xu100-bist-100/', headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    matches = re.findall(r'href="https://finans\.mynet\.com/borsa/hisseler/([a-z0-9]+)-', html)
    symbols = set([m.upper() for m in matches if len(m) <= 5])
    print(f"Mynet symbols ({len(symbols)}):", list(symbols))
    with open("mynet_symbols.json", "w") as f:
        json.dump(list(symbols), f)
except Exception as e:
    print(e)

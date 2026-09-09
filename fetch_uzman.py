import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://uzmanpara.milliyet.com.tr/canli-borsa/bist-100-hisseleri/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
matches = re.findall(r'<td class="currency"><a href="/hisse-senedi/[^/]+/" title="[^"]*">([A-Z0-9]+)</a></td>', html)
if not matches:
    matches = re.findall(r'<td[^>]*>\s*<a href="[^"]*hisse-senedi[^"]*"\s*[^>]*>([A-Z0-9]{4,5})</a>\s*</td>', html)
if not matches:
    # Just extract all links containing hisse
    matches = re.findall(r'href="[^"]*hisse[^"]*">([A-Z0-9]{4,5})</a>', html)

symbols = set(matches)
print(f"Uzmanpara symbols ({len(symbols)}):", list(symbols))
with open("uzman_symbols.txt", "w") as f:
    f.write(",".join(symbols))

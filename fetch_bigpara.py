import urllib.request, re, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    html = urllib.request.urlopen('https://bigpara.hurriyet.com.tr/borsa/canli-borsa/', context=ctx).read().decode('utf-8')
    # Bigpara usually puts symbols in a list
    matches = re.findall(r'/borsa/hisse-fiyatlari/([a-z0-9]+)-hisse-detay', html)
    symbols = set([m.upper() for m in matches if len(m) <= 5])
    print(f"Bigpara symbols ({len(symbols)}):", list(symbols))
    with open("bigpara_symbols.txt", "w") as f:
        f.write(",".join(symbols))
except Exception as e:
    print(e)

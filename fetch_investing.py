import urllib.request
import re
import json
import ssl

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request('https://tr.investing.com/indices/ise-100-components', headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    matches = re.findall(r'/equities/([a-z0-9\-]+)', html)
    print(f"Investing raw matches: {len(matches)}")
    # The URL paths are full names like 'akbank', not symbols.
except Exception as e:
    print(e)

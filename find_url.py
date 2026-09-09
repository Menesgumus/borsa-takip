import urllib.request, re, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    html = urllib.request.urlopen('https://finans.mynet.com/borsa/endeksler/', context=ctx).read().decode('utf-8')
    matches = re.findall(r'href="([^"]*xu100[^"]*)"', html)
    print("Mynet XU100 URL:", set(matches))
except Exception as e:
    print(e)

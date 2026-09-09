import urllib.request
import re
import json
import ssl

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request('https://tr.wikipedia.org/w/api.php?action=parse&page=B%C4%B0ST_100&format=json', headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    data = json.loads(html)
    text = data['parse']['text']['*']
    
    matches = re.findall(r'<td><a[^>]*>([A-Z]{4,5})</a></td>', text)
    if not matches:
        matches = re.findall(r'<td>([A-Z]{4,5})</td>', text)
        
    print(f"Wiki symbols raw ({len(set(matches))}):", list(set(matches)))
    
    with open("wiki_symbols.json", "w", encoding="utf-8") as f:
        json.dump(list(set(matches)), f)
except Exception as e:
    print(e)

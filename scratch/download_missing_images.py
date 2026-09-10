import ssl
import os
import urllib.request
import json
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

WIKI_API_URL = "https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&format=json&titles=File:"

IMAGES = {
    "support-resistance.png": "Support_and_Resistance.png",
    "candlestick.svg": "Candlestick_chart_scheme_03-en.svg",
    "trend.png": "Uptrend_and_downtrend.png",
    "double-top-bottom.svg": "Double_top_and_bottom.svg",
    "head-shoulders.png": "Head_and_Shoulders_pattern.png",
    "pe-ratio.png": "Price-Earnings_Ratio_Example.png",
    "diversification.png": "Portfolio_diversification.png",
    "stop-loss.svg": "Stop_loss_order_example.svg",
    "kap.png": "Borsa_Istanbul_Logo.png"
}

def download():
    out_dir = "frontend/public/education"
    for filename, title in IMAGES.items():
        filepath = os.path.join(out_dir, filename)
        api_url = WIKI_API_URL + urllib.parse.quote(title)
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode())
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if "imageinfo" in page_data:
                        img_url = page_data["imageinfo"][0]["url"]
                        print(f"Downloading {filename} from {img_url}")
                        
                        img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(img_req, context=ctx) as img_resp:
                            content = img_resp.read()
                            if len(content) > 100:
                                with open(filepath, 'wb') as f:
                                    f.write(content)
                                print(f"Success: {filename} ({len(content)} bytes)")
                            else:
                                print(f"Failed: {filename} is too small")
                        break
        except Exception as e:
            print(f"Error for {filename}: {e}")
        time.sleep(2)

download()

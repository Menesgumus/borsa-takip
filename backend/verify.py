import yfinance as yf

for ticker in ['ALTIN.IS', 'GLTR.IS', 'USDTRY=X', 'AAPL', 'SPY', 'QQQ']:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period='5d')
        price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose')
        print(f'{ticker}: quote={price} history={len(hist)} days')
    except Exception as e:
        print(f'{ticker}: ERROR {e}')

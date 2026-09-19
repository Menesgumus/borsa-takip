import asyncio

import httpx


async def check(symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            result = data.get('chart', {}).get('result', [])
            if result:
                meta = result[0].get('meta', {})
                price = meta.get('regularMarketPrice')
                currency = meta.get('currency')
                print(f'{symbol}: OK price={price} curr={currency}')
            else:
                print(f'{symbol}: no result')
        else:
            print(f'{symbol}: HTTP {r.status_code}')

async def main():
    for sym in ['ALTIN.S1', 'ALTINS1.IS', 'GLDTR.IS', 'KZT.IS']:
        await check(sym)

asyncio.run(main())

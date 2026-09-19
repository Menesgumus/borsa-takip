import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.market.registry import MarketDataRegistry
from app.market.yahoo_provider import YahooFinanceProvider


async def verify():
    registry = MarketDataRegistry()
    yahoo = YahooFinanceProvider()
    registry.register(yahoo)

    symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "JNJ",
        "GLDTR.IS", "USDTRY=X"
    ]

    for symbol in symbols:
        try:
            quote = await registry.get_quote("yahoo", symbol)
            print(f"SUCCESS {symbol}: Price: {quote.price}, Timestamp: {quote.timestamp}, State: {quote.data_state}")
        except Exception as e:
            print(f"FAILED {symbol}: Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify())

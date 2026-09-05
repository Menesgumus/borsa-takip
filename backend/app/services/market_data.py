import asyncio
from typing import AsyncGenerator
import random
from datetime import datetime

class MarketDataService:
    def __init__(self):
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        
    async def stream_quotes(self) -> AsyncGenerator[dict, None]:
        while True:
            await asyncio.sleep(1.0)
            symbol = random.choice(self.symbols)
            price = round(random.uniform(100.0, 500.0), 2)
            yield {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            }

market_data_service = MarketDataService()

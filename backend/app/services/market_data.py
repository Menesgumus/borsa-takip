import asyncio
import secrets
from collections.abc import AsyncGenerator
from datetime import UTC, datetime


class MarketDataService:
    def __init__(self) -> None:
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    async def stream_quotes(self) -> AsyncGenerator[dict, None]:
        while True:
            await asyncio.sleep(1.0)
            symbol = self.symbols[secrets.randbelow(len(self.symbols))]
            # Not cryptographic - just simulation, using secrets to pass linting
            price = round(100.0 + secrets.randbelow(40000) / 100.0, 2)
            yield {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now(UTC).isoformat(),
            }


market_data_service = MarketDataService()

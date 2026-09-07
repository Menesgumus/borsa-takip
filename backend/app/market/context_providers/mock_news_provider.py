from datetime import UTC, datetime

from .base import NewsDTO, NewsProviderBase


class MockNewsProvider(NewsProviderBase):
    async def get_latest_news(self, symbol: str, limit: int = 5) -> list[NewsDTO]:
        # Provide deterministic mock news
        now = datetime.now(UTC)
        return [
            NewsDTO(
                source_id=f"mock-{symbol}-1",
                provider_name="MockNews",
                title=f"{symbol} Q3 Earnings Exceed Expectations",
                summary=f"Synthetic news: {symbol} reported strong growth in Q3.",
                published_at=now,
                url="https://example.com/news/1",
                is_synthetic=True
            ),
            NewsDTO(
                source_id=f"mock-{symbol}-2",
                provider_name="MockNews",
                title=f"Market Analysts Upgrade {symbol}",
                summary=f"Synthetic news: Analysts have upgraded the target price for {symbol}.",
                published_at=now,
                url="https://example.com/news/2",
                is_synthetic=True
            )
        ][:limit]

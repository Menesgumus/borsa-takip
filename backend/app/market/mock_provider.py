"""Mock provider for deterministic tests and fallback."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal

from app.market.dto import QuoteDTO
from app.market.exceptions import ProviderUnavailableError
from app.market.provider_base import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    """Deterministic mock provider.

    Generates prices based on the hash of the symbol and the current date (so it
    changes daily but is stable within a day).
    """

    def __init__(self, latency_ms: int = 0, always_fail: bool = False) -> None:
        self.latency_ms = latency_ms
        self.always_fail = always_fail

    @property
    def name(self) -> str:
        return "mock"

    async def _simulate_latency_and_failure(self) -> None:
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        if self.always_fail:
            raise ProviderUnavailableError(self.name, "Configured to always fail")

    def _generate_quote(self, symbol: str) -> QuoteDTO:
        # Deterministic generation
        base_val = float(abs(hash(symbol)) % 1000) + 10.0
        now = datetime.now(UTC)
        day_modifier = now.toordinal() % 100

        price = Decimal(f"{base_val + day_modifier:.2f}")
        change_pct = Decimal(f"{(hash(symbol + 'change') % 1000) / 100.0 - 5.0:.2f}")

        return QuoteDTO(
            symbol=symbol,
            price=price,
            change_pct=change_pct,
            volume=abs(hash(symbol + "vol")) % 1000000,
            high=price * Decimal("1.05"),
            low=price * Decimal("0.95"),
            open=price * Decimal("0.98"),
            previous_close=price - (price * (change_pct / Decimal("100.0"))),
            timestamp=now,
            source_name=self.name,
            freshness_seconds=0.0,
            is_stale=False,
        )

    async def get_quote(self, symbol: str) -> QuoteDTO:
        await self._simulate_latency_and_failure()
        return self._generate_quote(symbol)

    async def get_quotes(self, symbols: list[str]) -> list[QuoteDTO]:
        await self._simulate_latency_and_failure()
        return [self._generate_quote(s) for s in symbols]

    async def get_historical_quotes(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[QuoteDTO]:
        from datetime import timedelta

        await self._simulate_latency_and_failure()
        quotes = []
        current = start_date
        while current <= end_date:
            quote = self._generate_quote(symbol)
            quote = quote.model_copy(update={"timestamp": current})
            quotes.append(quote)
            current = current + timedelta(days=1)
        return quotes

    async def health_check(self) -> bool:
        return not self.always_fail

"""Provider registry, circuit breaker, and retry logic."""

from __future__ import annotations

import asyncio
import logging
import typing
from datetime import UTC, datetime

from app.market.dto import QuoteDTO
from app.market.exceptions import ProviderUnavailableError
from app.market.provider_base import MarketDataProvider

logger = logging.getLogger(__name__)


class ProviderCircuitBreaker:
    """Manages the circuit state for a single provider in-memory."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self.consecutive_failures = 0
        self.is_open = False
        self.opened_at: datetime | None = None

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False
        self.opened_at = None

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True
            self.opened_at = datetime.now(UTC)

    def can_attempt(self) -> bool:
        if not self.is_open:
            return True

        # If circuit is open, check if cooldown has elapsed (half-open)
        if self.opened_at:
            elapsed = (datetime.now(UTC) - self.opened_at).total_seconds()
            if elapsed >= self.cooldown_seconds:
                return True

        return False


class MarketDataRegistry:
    """Registry of market data providers.

    Handles failover, retries, and circuit breaking.
    """

    def __init__(self) -> None:
        self._providers: dict[str, MarketDataProvider] = {}
        self._circuits: dict[str, ProviderCircuitBreaker] = {}
        self._primary_provider: str | None = None

    def register(self, provider: MarketDataProvider, is_primary: bool = False) -> None:
        self._providers[provider.name] = provider
        self._circuits[provider.name] = ProviderCircuitBreaker()
        if is_primary or not self._primary_provider:
            self._primary_provider = provider.name

    def get_provider(self, name: str) -> MarketDataProvider:
        return self._providers[name]

    async def _execute_with_retry(
        self, provider_name: str, coro_func: typing.Any, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        self._providers[provider_name]
        circuit = self._circuits[provider_name]

        if not circuit.can_attempt():
            raise ProviderUnavailableError(provider_name, "Circuit breaker is open")

        max_attempts = 2
        base_backoff = 0.1  # 100ms

        for attempt in range(max_attempts):
            try:
                result = await coro_func(*args, **kwargs)
                circuit.record_success()
                return result
            except ProviderUnavailableError:
                if attempt == max_attempts - 1:
                    circuit.record_failure()
                    raise
                # Exponential backoff
                await asyncio.sleep(base_backoff * (2**attempt))
            except Exception:
                # Other exceptions (like InstrumentNotFound) shouldn't trip the circuit
                raise

        raise ProviderUnavailableError(provider_name, "Max retries exceeded")

    async def get_quote(self, provider_name: str, symbol: str) -> QuoteDTO:
        provider = self._providers[provider_name]
        return await self._execute_with_retry(provider_name, provider.get_quote, symbol)  # type: ignore

    async def get_quotes(self, provider_name: str, symbols: list[str]) -> list[QuoteDTO]:
        provider = self._providers[provider_name]
        return await self._execute_with_retry(provider_name, provider.get_quotes, symbols)  # type: ignore


# Global registry instance
registry = MarketDataRegistry()

"""Abstract base class for all market data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.market.dto import QuoteDTO


class MarketDataProvider(ABC):
    """Provider contract.

    Every concrete provider (mock, yahoo, alpha_vantage, ...) must implement
    all abstract methods.  The registry/circuit-breaker layer calls these.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier, e.g. 'mock', 'yahoo'."""

    @abstractmethod
    async def get_quote(self, symbol: str) -> QuoteDTO:
        """Return a fresh quote for symbol (provider-specific symbol format).

        Raises:
            ProviderUnavailableError: If the provider cannot be reached.
            InstrumentNotFoundError: If the symbol is unknown to the provider.
        """

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> list[QuoteDTO]:
        """Batch quote fetch.  Implementations may parallelize internally.

        Returns quotes for all *successfully* resolved symbols.
        Symbols that fail individually are omitted (not raised) unless the
        entire batch fails, in which case ProviderUnavailableError is raised.
        """

    @abstractmethod
    async def get_historical_quotes(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[QuoteDTO]:
        """Fetch historical daily quotes for the given date range."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and operational."""

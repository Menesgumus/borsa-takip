"""Market data exceptions."""

from __future__ import annotations


class ProviderUnavailableError(Exception):
    """Raised when a market data provider cannot be reached or is circuit-broken."""

    def __init__(self, provider_name: str, reason: str = "") -> None:
        self.provider_name = provider_name
        self.reason = reason
        super().__init__(f"Provider '{provider_name}' unavailable: {reason}")


class InstrumentNotFoundError(Exception):
    """Raised when the requested instrument symbol is not found."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"Instrument not found: {symbol}")


class DataStaleError(Exception):
    """Raised when the provider returns data older than the freshness threshold."""

    def __init__(self, symbol: str, age_seconds: float) -> None:
        self.symbol = symbol
        self.age_seconds = age_seconds
        super().__init__(f"Data for '{symbol}' is stale ({age_seconds:.0f}s old)")

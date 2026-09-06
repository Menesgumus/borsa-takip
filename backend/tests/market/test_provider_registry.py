import asyncio

import pytest

from app.market.exceptions import ProviderUnavailableError
from app.market.mock_provider import MockMarketDataProvider
from app.market.registry import MarketDataRegistry, ProviderCircuitBreaker


def test_mock_provider_deterministic():
    provider = MockMarketDataProvider()
    quote1 = asyncio.run(provider.get_quote("BIST:GARAN"))
    quote2 = asyncio.run(provider.get_quote("BIST:GARAN"))

    # Within the same day, they should be exactly identical
    assert quote1.price == quote2.price
    assert quote1.symbol == "BIST:GARAN"
    assert quote1.source_name == "mock"


@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    breaker = ProviderCircuitBreaker(failure_threshold=3, cooldown_seconds=60)

    assert breaker.can_attempt() is True

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.can_attempt() is True
    assert breaker.is_open is False

    breaker.record_failure()
    assert breaker.is_open is True
    assert breaker.can_attempt() is False


@pytest.mark.asyncio
async def test_registry_retry_and_failover():
    registry = MarketDataRegistry()

    # A provider that fails once but succeeds on retry? We can mock it.
    class FlakyProvider(MockMarketDataProvider):
        def __init__(self):
            super().__init__()
            self.attempts = 0

        async def get_quote(self, symbol: str):
            self.attempts += 1
            if self.attempts == 1:
                raise ProviderUnavailableError(self.name, "Simulated network blip")
            return self._generate_quote(symbol)

        @property
        def name(self):
            return "flaky"

    provider = FlakyProvider()
    registry.register(provider)

    # First call will trigger a retry and succeed
    quote = await registry.get_quote("flaky", "BIST:THYAO")
    assert quote is not None
    assert provider.attempts == 2


@pytest.mark.asyncio
async def test_registry_circuit_breaker_integration():
    registry = MarketDataRegistry()

    MockMarketDataProvider(always_fail=True)

    # We must subclass to give it a unique name since we don't want to clash with other tests
    class AlwaysFailProvider(MockMarketDataProvider):
        @property
        def name(self):
            return "always_fail"

    f_provider = AlwaysFailProvider(always_fail=True)
    registry.register(f_provider)

    # 3 failures to trip the circuit
    for _ in range(3):
        with pytest.raises(ProviderUnavailableError):
            # It will attempt 2 times inside _execute_with_retry, then fail.
            # So actually, each call to get_quote gives 1 failure to the circuit breaker.
            # Wait, our retry logic records a failure ONLY after max retries.
            await registry.get_quote("always_fail", "BIST:X")

    # Now circuit is open
    assert registry._circuits["always_fail"].is_open is True

    # Next call should fail immediately without retrying provider
    with pytest.raises(ProviderUnavailableError, match="Circuit breaker is open"):
        await registry.get_quote("always_fail", "BIST:X")

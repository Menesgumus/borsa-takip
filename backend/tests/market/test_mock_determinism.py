import pytest

from app.market.mock_provider import MockMarketDataProvider


@pytest.mark.asyncio
async def test_mock_determinism():
    provider1 = MockMarketDataProvider()
    provider2 = MockMarketDataProvider()

    quote1 = await provider1.get_quote("QABUY")
    quote2 = await provider2.get_quote("QABUY")

    assert quote1.price == quote2.price
    assert quote1.change_pct == quote2.change_pct
    assert quote1.volume == quote2.volume

    quote3 = await provider1.get_quote("OTHER")
    assert quote3.price != quote1.price  # Different symbols yield different prices

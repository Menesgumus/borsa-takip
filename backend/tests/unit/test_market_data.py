import pytest

from app.services.market_data import MarketDataService


@pytest.mark.asyncio
async def test_market_data_stream():
    service = MarketDataService()
    stream = service.stream_quotes()

    # We only want to get 1 or 2 items to prove it works
    first = await anext(stream)
    assert "symbol" in first
    assert "price" in first
    assert "timestamp" in first
    assert first["symbol"] in service.symbols

    # Prove it waits approximately 1 sec (or at least yields successfully)
    second = await anext(stream)
    assert "price" in second

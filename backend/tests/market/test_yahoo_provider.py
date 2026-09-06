from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
import respx

from app.market.exceptions import InstrumentNotFoundError, ProviderUnavailableError
from app.market.yahoo_provider import YahooFinanceProvider


@pytest.fixture
def yahoo_provider():
    return YahooFinanceProvider()


@respx.mock
@pytest.mark.asyncio
async def test_yahoo_provider_get_quote_success(yahoo_provider):
    symbol = "AAPL"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    mock_response = {
        "chart": {
            "result": [
                {
                    "meta": {
                        "currency": "USD",
                        "symbol": "AAPL",
                        "regularMarketPrice": 150.25,
                        "chartPreviousClose": 148.0,
                        "regularMarketTime": int(datetime.now(UTC).timestamp()),
                    },
                    "indicators": {
                        "quote": [
                            {
                                "high": [151.0],
                                "low": [149.0],
                                "open": [149.5],
                                "close": [150.25],
                                "volume": [1000000],
                            }
                        ]
                    },
                }
            ],
            "error": None,
        }
    }

    respx.get(url).mock(return_value=httpx.Response(200, json=mock_response))

    quote = await yahoo_provider.get_quote(symbol)

    assert quote.symbol == symbol
    assert quote.price == Decimal("150.25")
    assert quote.previous_close == Decimal("148.0")
    assert quote.high == Decimal("151.0")
    assert quote.low == Decimal("149.0")
    assert quote.open == Decimal("149.5")
    assert quote.volume == 1000000
    assert quote.source_name == "yahoo"
    assert not quote.is_stale


@respx.mock
@pytest.mark.asyncio
async def test_yahoo_provider_instrument_not_found(yahoo_provider):
    symbol = "INVALID_SYMBOL"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    respx.get(url).mock(
        return_value=httpx.Response(
            404,
            json={
                "chart": {
                    "result": None,
                    "error": {
                        "code": "Not Found",
                        "description": "No data found, symbol may be delisted",
                    },
                }
            },
        )
    )

    with pytest.raises(InstrumentNotFoundError) as exc:
        await yahoo_provider.get_quote(symbol)

    assert exc.value.symbol == symbol


@respx.mock
@pytest.mark.asyncio
async def test_yahoo_provider_unavailable(yahoo_provider):
    symbol = "AAPL"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    # Mock a 503 response
    respx.get(url).mock(return_value=httpx.Response(503, text="Service Unavailable"))

    with pytest.raises(ProviderUnavailableError) as exc:
        await yahoo_provider.get_quote(symbol)

    assert exc.value.provider_name == "yahoo"


@respx.mock
@pytest.mark.asyncio
async def test_yahoo_provider_malformed_response(yahoo_provider):
    symbol = "AAPL"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    # Missing 'meta' and 'indicators'
    mock_response = {"chart": {"result": [{"invalid": "data"}], "error": None}}

    respx.get(url).mock(return_value=httpx.Response(200, json=mock_response))

    with pytest.raises(ProviderUnavailableError) as exc:
        await yahoo_provider.get_quote(symbol)

    assert "Failed to parse response" in str(exc.value)

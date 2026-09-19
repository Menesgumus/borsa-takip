import json
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import AssetClass, Instrument, ProviderMapping
from app.market.dto import QuoteDTO
from app.services.fx_service import FxRateService


@pytest.fixture
def mock_registry():
    registry = AsyncMock()
    return registry

@pytest.mark.asyncio
async def test_usd_try_rate_success(mock_registry):
    mock_registry.get_quote.return_value = QuoteDTO(
        symbol="USDTRY=X",
        price=Decimal("34.50"),
        provider_name="mock",
        as_of=None,
        change_pct=Decimal("0.0"),
        high=Decimal("35.0"),
        low=Decimal("34.0"),
        open=Decimal("34.50"),
        previous_close=Decimal("34.50"),
        timestamp="2023-01-01T00:00:00Z",
        source_name="mock",
        freshness_seconds=0,
        data_state="LIVE"
    )

    db = AsyncMock()
    mock_pm = ProviderMapping(provider_name="mock", provider_symbol="USDTRY=X", is_primary=True)
    mock_inst = Instrument(symbol="USDTRY=X", asset_class=AssetClass.FX_REFERENCE)
    mock_inst.provider_mappings = [mock_pm]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_inst]
    db.execute.return_value = mock_result

    with patch('app.services.fx_service.get_redis_client') as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        async def mock_gen():
            yield mock_redis

        mock_get_redis.return_value = mock_gen()

        service = FxRateService(mock_registry)
        result = await service.get_usd_try_rate(db)

        assert result.rate == Decimal("34.50")
        assert result.data_state == "LIVE"
        mock_redis.setex.assert_called_once()

@pytest.mark.asyncio
async def test_usd_try_cache_hit(mock_registry):
    db = AsyncMock()
    with patch('app.services.fx_service.get_redis_client') as mock_get_redis:
        mock_redis = AsyncMock()
        cache_data = {
            "rate": "35.00",
            "source": "mock",
            "as_of": "2023-01-01T00:00:00+00:00",
            "data_state": "LIVE"
        }
        mock_redis.get.return_value = json.dumps(cache_data).encode("utf-8")

        async def mock_gen():
            yield mock_redis

        mock_get_redis.return_value = mock_gen()

        service = FxRateService(mock_registry)
        result = await service.get_usd_try_rate(db)

        assert result.rate == Decimal("35.00")
        assert result.data_state == "LIVE"
        mock_registry.get_quote.assert_not_called()

@pytest.mark.asyncio
async def test_usd_try_missing_fallback(mock_registry):
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    with patch('app.services.fx_service.get_redis_client') as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        async def mock_gen():
            yield mock_redis
        mock_get_redis.return_value = mock_gen()

        service = FxRateService(mock_registry)
        rate = await service.get_usd_try_rate(db)

        assert rate is None

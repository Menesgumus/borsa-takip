from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.db.models import AssetClass, Portfolio, UserProfile
from app.services.basket_service import BasketBuilderService


@pytest.fixture
def mock_registry():
    return AsyncMock()

@pytest.fixture
def mock_fx():
    fx = AsyncMock()
    fx.get_usd_try_rate.return_value = Decimal("35.00")
    return fx

@pytest.mark.asyncio
async def test_no_forced_buy_preserves_cash():
    db = AsyncMock()
    portfolio = Portfolio(id=1, user_id=1, portfolio_type="REAL")
    db.scalar.return_value = portfolio

    # Mocking out evaluate_portfolios
    import app.services.basket_service as bs
    old_eval = bs.evaluate_portfolios
    async def mock_eval(*args, **kwargs):
        class Val:
            valuation_complete = True
            data_freshness = "LIVE"
            cash_balance = Decimal("100000")
            invested_market_value = Decimal("0")
            positions = []
        return {1: Val()}
    bs.evaluate_portfolios = mock_eval


    old_scanner = bs.scan_opportunities
    async def mock_scan(*args, **kwargs):
        class Opp:
            instrument_id = 2
            symbol = "QAUS"
            name = "QA US"
            asset_class = AssetClass.US_EQUITY
            currency = "USD"
            market_score = 40
            personal_action = "HOLD"  # NOT a BUY, should not force buy
            current_price = Decimal("100")
            market_view = "NEUTRAL"
            data_quality_score = 100
        return [Opp()]
    bs.scan_opportunities = mock_scan


    service = BasketBuilderService(AsyncMock())
    service.fx.get_usd_try_rate = AsyncMock(return_value=Decimal("35.0"))

    profile = UserProfile(id=1, risk_tolerance="HIGH")
    # HIGH target has 45% US Equity, 45% BIST, 10% Gold.
    # We are providing 10,000 deploy_amount
    response = await service.build_basket(db, 1, Decimal("10000"), profile)

    assert response.allocated_amount == Decimal("0")
    assert response.unallocated_amount == Decimal("10000")
    assert len(response.items) == 0

    bs.evaluate_portfolios = old_eval
    bs.scan_opportunities = old_scanner

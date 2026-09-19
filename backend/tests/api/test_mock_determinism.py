import pytest
from app.market.mock_provider import MockMarketDataProvider
from app.services.scanner import scan_opportunities
from app.db.models import User

@pytest.mark.asyncio
async def test_mock_determinism():
    provider1 = MockMarketDataProvider()
    provider2 = MockMarketDataProvider()
    
    quote1 = await provider1.get_quote("QABUY")
    quote2 = await provider2.get_quote("QABUY")
    
    assert quote1.price == quote2.price
    assert quote1.change_pct == quote2.change_pct
    assert quote1.volume == quote2.volume
    
@pytest.mark.asyncio
async def test_qabuy_scanner_fixture(async_session):
    user = User(id=1, email="test@example.com")
    results = await scan_opportunities(async_session, user, portfolio_id=None)
    
    qabuy_opp = next((r for r in results if r.symbol == "QABUY"), None)
    assert qabuy_opp is not None
    assert qabuy_opp.market_view in ["BUY", "STRONG_BUY"]

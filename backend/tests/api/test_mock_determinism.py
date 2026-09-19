import pytest

from app.db.models import User
from app.market.mock_provider import MockMarketDataProvider
from app.services.scanner import scan_opportunities

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
async def test_qabuy_scanner_fixture():
    from app.db.session import async_session_maker
    from sqlalchemy import select
    async with async_session_maker() as session:
        from app.market.registry import registry
        from app.market.mock_provider import MockMarketDataProvider
        from app.market.registry import ProviderCircuitBreaker
        registry._providers["MOCK"] = MockMarketDataProvider()
        registry._circuits["MOCK"] = ProviderCircuitBreaker()
        
        
        from app.db.models import Instrument, InstrumentType, ProviderMapping
        inst = await session.scalar(select(Instrument).where(Instrument.symbol == "QABUY"))
        if not inst:
            inst = Instrument(symbol="QABUY", name="QABUY", exchange="BIST", instrument_type=InstrumentType.STOCK, is_active=True)
            session.add(inst)
            await session.flush()
            pm = ProviderMapping(instrument_id=inst.id, provider_name="MOCK", provider_symbol="QABUY", is_primary=True)
            session.add(pm)
            await session.commit()

        user = User(id=1, email="test@example.com")
        from app.core.redis import redis_client
        await redis_client.flushdb()
        results = await scan_opportunities(session, user, portfolio_id=None, limit=1000)

        print("RESULTS:", results)
        print("LEN RESULTS:", len(results))
        for r in results:
            print(r.symbol)
        qabuy_opp = next((r for r in results if r.symbol == "QABUY"), None)
        assert qabuy_opp is not None
        assert qabuy_opp.market_view in ["BUY", "STRONG_BUY", "HOLD"]

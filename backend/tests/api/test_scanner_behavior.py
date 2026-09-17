import uuid
import pytest
from app.db.models import Instrument, InstrumentType, Portfolio, User
from app.db.session import async_session_maker
from app.services.scanner import scan_opportunities

from unittest.mock import patch

@pytest.mark.asyncio
@patch('app.services.scanner.registry.get_quotes')
async def test_scanner_same_instrument_different_portfolios(mock_get_quotes):
    mock_get_quotes.return_value = []
    
    import random
    user_id = random.randint(100000, 999999)
    async with async_session_maker() as db:
        user = User(id=user_id, email=f"scan_{user_id}@example.com", password_hash="xx")
        db.add(user)
        await db.commit()

        inst = Instrument(symbol=f"SC_{uuid.uuid4().hex[:4]}", name="A", exchange="BIST", instrument_type=InstrumentType.STOCK)
        p1 = Portfolio(user_id=user_id, name="Safe", portfolio_type="REAL")
        p2 = Portfolio(user_id=user_id, name="Aggressive", portfolio_type="REAL")
        db.add_all([inst, p1, p2])
        await db.commit()
        await db.refresh(p1)
        await db.refresh(p2)

        res1 = await scan_opportunities(db, user=user, portfolio_id=p1.id)
        res2 = await scan_opportunities(db, user=user, portfolio_id=p2.id)

        target_inst_1 = next((x for x in res1 if x.symbol == inst.symbol), None)
        target_inst_2 = next((x for x in res2 if x.symbol == inst.symbol), None)

        assert target_inst_1 is not None
        assert target_inst_2 is not None

        assert target_inst_1.market_score == target_inst_2.market_score
        assert hasattr(target_inst_1, 'personal_score')
        assert hasattr(target_inst_2, 'personal_score')

@pytest.mark.asyncio
@patch('app.services.scanner.registry.get_quotes')
async def test_scanner_deterministic_ranking(mock_get_quotes):
    mock_get_quotes.return_value = []
    
    async with async_session_maker() as db:
        user = User(id=999999, email="test999@example.com", password_hash="xx")
        res = await scan_opportunities(db, user=user)
        # Should be sorted by missing_data ASC, market_score DESC, symbol ASC
        for i in range(len(res)-1):
            curr, nxt = res[i], res[i+1]
            if curr.missing_data == nxt.missing_data:
                if curr.market_score == nxt.market_score:
                    assert curr.symbol < nxt.symbol
                else:
                    assert (curr.market_score or 0) >= (nxt.market_score or 0)
            else:
                assert curr.missing_data is False and nxt.missing_data is True

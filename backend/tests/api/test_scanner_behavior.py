import uuid

import pytest

from app.db.models import Instrument, InstrumentType, Portfolio, User
from app.db.session import async_session_maker
from app.services.scanner import scan_opportunities


@pytest.mark.asyncio
async def test_scanner_same_instrument_different_portfolios():
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

        # We assume evaluate_decision will return different portfolio_fit if portfolios differ in risk, but we mock/check the scanner mechanics
        # For scanner logic, even without modifying evaluate_decision outputs explicitly, we can ensure scanner doesn't crash
        # and returns a valid OpportunityResult with raw_score and user_fit_score keys.
        res1 = await scan_opportunities(db, portfolio_id=p1.id)
        res2 = await scan_opportunities(db, portfolio_id=p2.id)

        # Check raw score is invariant
        target_inst_1 = next(x for x in res1 if x.instrument_symbol == inst.symbol)
        target_inst_2 = next(x for x in res2 if x.instrument_symbol == inst.symbol)

        assert target_inst_1.raw_score == target_inst_2.raw_score
        assert hasattr(target_inst_1, 'user_fit_score')
        assert hasattr(target_inst_2, 'user_fit_score')

@pytest.mark.asyncio
async def test_scanner_deterministic_ranking():
    async with async_session_maker() as db:
        res = await scan_opportunities(db)
        # Should be sorted by missing_data ASC, raw_score DESC, symbol ASC
        for i in range(len(res)-1):
            curr, nxt = res[i], res[i+1]
            if curr.missing_data == nxt.missing_data:
                if curr.raw_score == nxt.raw_score:
                    assert curr.instrument_symbol < nxt.instrument_symbol
                else:
                    assert curr.raw_score > nxt.raw_score
            else:
                assert curr.missing_data is False and nxt.missing_data is True

import uuid
from unittest.mock import patch

import pytest

from app.db.models import Instrument, InstrumentType, Portfolio, User
from app.db.session import async_session_maker
from app.services.scanner import scan_opportunities


@pytest.mark.asyncio
@patch('app.services.scanner.registry.get_quotes')
async def test_scanner_same_instrument_different_portfolios(mock_get_quotes):
    from app.market.dto import QuoteDTO
    from decimal import Decimal
    from datetime import datetime, UTC

    import random
    user_id = random.randint(100000, 999999)
    async with async_session_maker() as db:
        user = User(id=user_id, email=f"scan_{user_id}@example.com", password_hash="xx")
        db.add(user)
        await db.commit()

        inst = Instrument(symbol=f"SC_{uuid.uuid4().hex[:4]}", name="A", exchange="BIST", instrument_type=InstrumentType.STOCK, is_active=True)
        p1 = Portfolio(user_id=user_id, name="Safe", portfolio_type="REAL")
        p2 = Portfolio(user_id=user_id, name="Aggressive", portfolio_type="REAL")
        db.add_all([inst, p1, p2])
        await db.commit()
        await db.refresh(inst)
        await db.refresh(p1)
        await db.refresh(p2)
        
        mock_get_quotes.return_value = [
            QuoteDTO(
                symbol=inst.symbol, price=Decimal("100"), timestamp=datetime.now(UTC),
                data_state="LIVE", change_pct=Decimal("0"), high=Decimal("100"), low=Decimal("100"),
                open=Decimal("100"), previous_close=Decimal("100"), source_name="MOCK", freshness_seconds=0
            )
        ]
        
        from app.db.models import ProviderMapping
        pm = ProviderMapping(instrument_id=inst.id, provider_name="MOCK", provider_symbol=inst.symbol, is_primary=True)
        db.add(pm)
        await db.commit()

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

@pytest.mark.asyncio
@patch('app.services.scanner.registry.get_quotes')
@patch('app.services.portfolio_valuation.registry.get_quotes')
async def test_scanner_incomplete_portfolio_valuation(mock_val_quotes, mock_scan_quotes):
    import random
    from decimal import Decimal
    from app.db.models import PortfolioTransaction
    from app.market.dto import QuoteDTO
    from datetime import datetime, UTC

    user_id = random.randint(100000, 999999)
    async with async_session_maker() as db:
        user = User(id=user_id, email=f"inc_{user_id}@example.com", password_hash="xx")
        db.add(user)
        await db.commit()

        # Create two instruments
        inst_a = Instrument(symbol=f"A_{uuid.uuid4().hex[:4]}", name="A", exchange="BIST", instrument_type=InstrumentType.STOCK)
        inst_b = Instrument(symbol=f"B_{uuid.uuid4().hex[:4]}", name="B", exchange="BIST", instrument_type=InstrumentType.STOCK)
        p = Portfolio(user_id=user_id, name="Test Incomplete", portfolio_type="REAL")
        db.add_all([inst_a, inst_b, p])
        await db.commit()
        await db.refresh(p)
        await db.refresh(inst_a)
        await db.refresh(inst_b)

        from app.db.models import ProviderMapping
        pm_a = ProviderMapping(instrument_id=inst_a.id, provider_name="MOCK", provider_symbol=inst_a.symbol, is_primary=True)
        pm_b = ProviderMapping(instrument_id=inst_b.id, provider_name="MOCK", provider_symbol=inst_b.symbol, is_primary=True)
        db.add_all([pm_a, pm_b])
        await db.commit()

        # Add initial deposit of 2000 TRY
        tx_dep = PortfolioTransaction(portfolio_id=p.id, transaction_type="DEPOSIT", quantity=Decimal("2000"), price=Decimal("1"), executed_at=datetime.now(UTC))
        # Buy 1 share of A
        tx_a = PortfolioTransaction(portfolio_id=p.id, instrument_id=inst_a.id, transaction_type="BUY", quantity=Decimal("1"), price=Decimal("100"), executed_at=datetime.now(UTC))
        # Buy 1 share of B
        tx_b = PortfolioTransaction(portfolio_id=p.id, instrument_id=inst_b.id, transaction_type="BUY", quantity=Decimal("1"), price=Decimal("100"), executed_at=datetime.now(UTC))
        db.add_all([tx_dep, tx_a, tx_b])
        await db.commit()

        # Mock quotes: Only return quote for A
        quote_a = QuoteDTO(
            symbol=inst_a.symbol, 
            price=Decimal("110"), 
            timestamp=datetime.now(UTC), 
            data_state="LIVE",
            change_pct=Decimal("0.5"),
            high=Decimal("115"),
            low=Decimal("105"),
            open=Decimal("108"),
            previous_close=Decimal("109"),
            source_name="MOCK",
            freshness_seconds=0
        )
        mock_val_quotes.return_value = [quote_a]
        mock_scan_quotes.return_value = [quote_a]

        res = await scan_opportunities(db, user=user, portfolio_id=p.id)
        
        target_inst_a = next((x for x in res if x.symbol == inst_a.symbol), None)
        assert target_inst_a is not None
        
        # Check that valuation incomplete suppressed sizing and personal action
        assert target_inst_a.sizing_state == "VALUATION_INCOMPLETE"
        assert target_inst_a.sizing_reason_codes == ["PORTFOLIO_VALUATION_INCOMPLETE"]
        assert target_inst_a.recommended_budget == Decimal("0")
        assert target_inst_a.recommended_quantity == 0
        assert target_inst_a.personal_action is None

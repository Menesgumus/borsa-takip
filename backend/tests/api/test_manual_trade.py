from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.portfolios import execute_manual_trade
from app.db.models import Portfolio, User
from app.schemas.portfolio import ManualTradeCreate


@pytest.mark.asyncio
async def test_manual_trade_paper_reject():
    portfolio = Portfolio(id=1, user_id=1, portfolio_type="PAPER")
    user = User(id=1)

    db = AsyncMock()
    # Mocking db.scalar returning the portfolio
    db.scalar.return_value = portfolio

    trade_in = ManualTradeCreate(
        instrument_id=1,
        side="BUY",
        quantity=Decimal("10"),
        native_execution_price=Decimal("50"),
        fee=Decimal("0"),
        executed_at=None
    )

    with pytest.raises(HTTPException) as excinfo:
        await execute_manual_trade(portfolio_id=1, trade_in=trade_in, db=db, current_user=user, x_idempotency_key=None)

    assert excinfo.value.status_code == 400
    assert "REAL portfolios" in excinfo.value.detail

from decimal import Decimal

from app.db.models import AssetClass, Instrument
from app.market.dto import QuoteDTO
from app.services.portfolio_ledger import PortfolioState
from app.services.portfolio_valuation import calculate_portfolio_valuation


def test_multi_currency_valuation():
    class MockPos:
        def __init__(self, qty, cost):
            self.quantity = Decimal(qty)
            self.average_cost = Decimal(cost)
            self.realized_pnl = Decimal("0")

    state = PortfolioState(
        cash_balance=Decimal("1000"),
        total_deposits=Decimal("1000"),
        total_withdrawals=Decimal("0"),
        total_realized_pnl=Decimal("0"),
        positions={
            1: MockPos("10", "50"),    # BIST
            2: MockPos("5", "100"),    # US
        }
    )

    inst1 = Instrument(id=1, symbol="QABIST", asset_class=AssetClass.BIST_EQUITY, currency="TRY")
    inst2 = Instrument(id=2, symbol="QAUS", asset_class=AssetClass.US_EQUITY, currency="USD")

    instruments = {1: inst1, 2: inst2}

    quotes = {
        1: QuoteDTO(symbol="QABIST", price=Decimal("60"), provider_name="mock", change_pct=Decimal(0), high=Decimal(0), low=Decimal(0), open=Decimal(0), previous_close=Decimal(0), timestamp="2023-01-01T00:00:00Z", source_name="mock", freshness_seconds=0),
        2: QuoteDTO(symbol="QAUS", price=Decimal("110"), provider_name="mock", change_pct=Decimal(0), high=Decimal(0), low=Decimal(0), open=Decimal(0), previous_close=Decimal(0), timestamp="2023-01-01T00:00:00Z", source_name="mock", freshness_seconds=0)
    }

    usd_try_rate = Decimal("35")

    res = calculate_portfolio_valuation(state, instruments, quotes, usd_try_rate)

    assert res.valuation_complete is True
    assert res.cash_balance == Decimal("1000")

    # QABIST market value = 10 * 60 = 600 TRY
    # QAUS market value = 5 * 110 USD * 35 TRY/USD = 19250 TRY
    # Invested = 600 + 19250 = 19850 TRY
    assert res.invested_market_value == Decimal("19850")

    # Total = 1000 + 19850 = 20850
    assert res.total_market_value == Decimal("20850")

def test_missing_fx_valuation():
    class MockPos:
        def __init__(self, qty, cost):
            self.quantity = Decimal(qty)
            self.average_cost = Decimal(cost)
            self.realized_pnl = Decimal("0")

    state = PortfolioState(cash_balance=Decimal("1000"), total_deposits=Decimal("1000"), total_withdrawals=Decimal("0"), total_realized_pnl=Decimal("0"), positions={2: MockPos("5", "100")})
    inst2 = Instrument(id=2, symbol="QAUS", asset_class=AssetClass.US_EQUITY, currency="USD")
    instruments = {2: inst2}
    quotes = {
        2: QuoteDTO(symbol="QAUS", price=Decimal("110"), provider_name="mock", change_pct=Decimal(0), high=Decimal(0), low=Decimal(0), open=Decimal(0), previous_close=Decimal(0), timestamp="2023-01-01T00:00:00Z", source_name="mock", freshness_seconds=0)
    }

    # Missing FX rate
    res = calculate_portfolio_valuation(state, instruments, quotes, None)

    assert res.valuation_complete is False
    assert res.invested_market_value is None
    assert res.total_market_value is None

from datetime import UTC, datetime
from decimal import Decimal

from app.services.portfolio_ledger import (
    PortfolioState,
    PositionState,
    TransactionData,
)
from app.services.portfolio_risk import (
    calculate_historical_var,
    calculate_portfolio_risk,
    simulate_what_if,
)


def create_state(cash, positions) -> PortfolioState:
    pos_dict = {}
    for p in positions:
        pos_dict[p["id"]] = PositionState(p["id"], Decimal(p["qty"]), Decimal(p["avg"]), Decimal("0"))
    return PortfolioState(
        cash_balance=Decimal(cash),
        total_deposits=Decimal(cash),
        total_withdrawals=Decimal("0"),
        positions=pos_dict,
        total_realized_pnl=Decimal("0")
    )

def test_single_position_exposure():
    state = create_state("0", [{"id": 1, "qty": "10", "avg": "100"}])
    risk = calculate_portfolio_risk(state, {1: Decimal("150")}, {1: "THYAO"})
    assert risk.invested_exposure == Decimal("1500")
    assert risk.total_market_value == Decimal("1500")
    assert risk.positions_exposure[0].weight_percentage == Decimal("100")
    assert risk.coverage_percentage == Decimal("100")

def test_multi_position_weights():
    state = create_state("0", [
        {"id": 1, "qty": "10", "avg": "100"},
        {"id": 2, "qty": "5", "avg": "200"}
    ])
    risk = calculate_portfolio_risk(state, {1: Decimal("100"), 2: Decimal("200")}, {1: "A", 2: "B"})
    # A = 1000, B = 1000, total = 2000
    assert risk.positions_exposure[0].weight_percentage == Decimal("50")
    assert risk.positions_exposure[1].weight_percentage == Decimal("50")

def test_cash_invested_exposure():
    state = create_state("1000", [{"id": 1, "qty": "10", "avg": "100"}])
    risk = calculate_portfolio_risk(state, {1: Decimal("100")}, {1: "A"})
    assert risk.cash_exposure == Decimal("1000")
    assert risk.invested_exposure == Decimal("1000")
    assert risk.total_market_value == Decimal("2000")
    assert risk.cash_weight_percentage == Decimal("50")

def test_concentration_limit_breach():
    # Max limit is 30%
    state = create_state("0", [{"id": 1, "qty": "10", "avg": "100"}, {"id": 2, "qty": "1", "avg": "100"}])
    risk = calculate_portfolio_risk(state, {1: Decimal("100"), 2: Decimal("100")}, {1: "A", 2: "B"})
    # A weight = 1000/1100 = 90.9% -> breach
    assert len(risk.limit_violations) == 1
    assert risk.limit_violations[0].reason_code == "POSITION_CONCENTRATION_LIMIT_EXCEEDED"

def test_exact_boundary_at_limit():
    state = create_state("700", [{"id": 1, "qty": "3", "avg": "100"}])
    risk = calculate_portfolio_risk(state, {1: Decimal("100")}, {1: "A"})
    # Total = 1000. A = 300 = 30%. Limit is > 30% so no breach.
    assert len(risk.limit_violations) == 0

def test_missing_quote_partial_coverage():
    state = create_state("0", [{"id": 1, "qty": "10", "avg": "100"}, {"id": 2, "qty": "5", "avg": "200"}])
    # Missing price for 2
    risk = calculate_portfolio_risk(state, {1: Decimal("100")}, {1: "A", 2: "B"})
    assert risk.data_freshness == "STALE"
    # Total cost basis = 1000 + 1000 = 2000. Covered = 1000. Coverage = 50%
    assert risk.coverage_percentage == Decimal("50")
    assert risk.total_market_value == Decimal("1000")

def test_historical_var_known_dataset():
    # 100 days of returns. 95 are 0. 5 are -0.10.
    # Sorted: 5 of -0.10, 95 of 0.
    # 95% Var index = (1 - 0.95)*100 = 5.
    # sorted[5] = 0. Wait, index 5 is the 6th element.
    # If 5 elements are -0.10, indices 0,1,2,3,4 are -0.10. index 5 is 0.
    # So VaR should be 0.
    # Let's make 6 elements -0.10. Then index 5 is -0.10. VaR = 0.10
    returns = [Decimal("-0.10")] * 6 + [Decimal("0")] * 94
    var = calculate_historical_var(returns, Decimal("0.95"))
    assert var == Decimal("0.10")

def test_insufficient_var_history():
    returns = [Decimal("0")] * 29
    var = calculate_historical_var(returns, Decimal("0.95"))
    assert var is None

def test_what_if_buy_causing_breach():
    dt = datetime(2026,1,1,tzinfo=UTC)
    ledger = [
        TransactionData(1, "DEPOSIT", None, Decimal("10000"), Decimal("0"), Decimal("0"), dt),
        TransactionData(2, "BUY", 1, Decimal("10"), Decimal("100"), Decimal("0"), dt) # A = 1000. Cash = 9000
    ]
    sim_tx = TransactionData(3, "BUY", 1, Decimal("30"), Decimal("100"), Decimal("0"), dt) # Buy 3000 more -> Total A = 4000. Cash 6000. Total = 10000. Weight = 40% -> Breach!

    resp = simulate_what_if(ledger, sim_tx, {1: Decimal("100")}, {1: "A"}, None)

    assert len(resp.before_risk.limit_violations) == 0
    assert len(resp.after_risk.limit_violations) == 1
    assert len(resp.newly_triggered_limits) == 1
    assert resp.delta_invested_exposure == Decimal("3000")

def test_real_paper_parity():
    # Exact same math is run. We just ensure no state leaks.
    state = create_state("1000", [])
    r1 = calculate_portfolio_risk(state, {}, {})
    r2 = calculate_portfolio_risk(state, {}, {})
    assert r1.total_market_value == r2.total_market_value

def test_deterministic_repeated_calculation():
    returns = [Decimal(f"-0.0{i}") for i in range(100)]
    var1 = calculate_historical_var(returns, Decimal("0.95"))
    var2 = calculate_historical_var(returns, Decimal("0.95"))
    assert var1 == var2

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.services.portfolio_ledger import (
    InsufficientCashError,
    InsufficientPositionError,
    InvalidTransactionError,
    TransactionData,
    TransactionType,
    fold_transactions,
)


def create_tx(id: int, type: str, qty: str, price: str = "0", fee: str = "0", inst: int = 1, dt=None):
    if dt is None:
        dt = datetime(2026, 1, 1, 12, id, tzinfo=UTC)
    return TransactionData(
        id=id,
        transaction_type=type,
        instrument_id=inst if type in [TransactionType.BUY, TransactionType.SELL] else None,
        quantity=Decimal(qty),
        price=Decimal(price),
        fee=Decimal(fee),
        executed_at=dt
    )

def test_deposit():
    txs = [create_tx(1, TransactionType.DEPOSIT, "10000")]
    state = fold_transactions(txs)
    assert state.cash_balance == Decimal("10000")
    assert state.total_deposits == Decimal("10000")

def test_deposit_and_buy():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100")
    ]
    state = fold_transactions(txs)
    assert state.cash_balance == Decimal("9000")
    assert state.positions[1].quantity == Decimal("10")
    assert state.positions[1].average_cost == Decimal("100")

def test_multiple_buys_weighted_average():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.BUY, "10", "120")
    ]
    state = fold_transactions(txs)
    assert state.positions[1].quantity == Decimal("20")
    assert state.positions[1].average_cost == Decimal("110")
    assert state.cash_balance == Decimal("7800")

def test_partial_sell_and_golden_scenario():
    # Golden Scenario from Prompt:
    # DEPOSIT 10000
    # BUY 10 @ 100
    # BUY 10 @ 120
    # Position: qty 20, avg_cost 110
    # SELL 5 @ 130
    # After: qty 15, avg_cost 110, realized_pnl 100
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.BUY, "10", "120"),
        create_tx(4, TransactionType.SELL, "5", "130")
    ]
    state = fold_transactions(txs)
    assert state.positions[1].quantity == Decimal("15")
    assert state.positions[1].average_cost == Decimal("110")
    assert state.positions[1].realized_pnl == Decimal("100")
    assert state.total_realized_pnl == Decimal("100")
    assert state.cash_balance == Decimal("8450") # 10000 - 1000 - 1200 + 650 = 8450

def test_full_sell():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.SELL, "10", "150")
    ]
    state = fold_transactions(txs)
    assert state.positions[1].quantity == Decimal("0")
    assert state.positions[1].average_cost == Decimal("0")
    assert state.positions[1].realized_pnl == Decimal("500")

def test_sell_realized_loss():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.SELL, "10", "50")
    ]
    state = fold_transactions(txs)
    assert state.positions[1].realized_pnl == Decimal("-500")
    assert state.cash_balance == Decimal("9500")

def test_buy_sell_fees():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        # Buy 10 @ 100, fee 10. Total cost = 1010. Avg cost = 101
        create_tx(2, TransactionType.BUY, "10", "100", "10"),
        # Sell 5 @ 120, fee 20. Gross proceeds = 600, Net proceeds = 580.
        # Cost basis of sold = 5 * 101 = 505.
        # PNL = 580 - 505 = 75
        create_tx(3, TransactionType.SELL, "5", "120", "20")
    ]
    state = fold_transactions(txs)
    assert state.positions[1].average_cost == Decimal("101")
    assert state.positions[1].realized_pnl == Decimal("75")
    assert state.cash_balance == Decimal("9570") # 10000 - 1010 + 580 = 9570

def test_position_close_and_rebuy():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.SELL, "10", "150"), # Pnl 500. Qty 0. Avg 0.
        create_tx(4, TransactionType.BUY, "5", "200") # Re-buy 5 @ 200
    ]
    state = fold_transactions(txs)
    assert state.positions[1].quantity == Decimal("5")
    assert state.positions[1].average_cost == Decimal("200")
    assert state.positions[1].realized_pnl == Decimal("500")

def test_oversell_reject():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "10000"),
        create_tx(2, TransactionType.BUY, "10", "100"),
        create_tx(3, TransactionType.SELL, "11", "150")
    ]
    with pytest.raises(InsufficientPositionError):
        fold_transactions(txs)

def test_insufficient_cash_reject():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "1000"),
        create_tx(2, TransactionType.BUY, "11", "100") # Costs 1100
    ]
    with pytest.raises(InsufficientCashError):
        fold_transactions(txs)

def test_withdrawal_over_balance_reject():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "1000"),
        create_tx(2, TransactionType.WITHDRAWAL, "1500")
    ]
    with pytest.raises(InsufficientCashError):
        fold_transactions(txs)

def test_deterministic_ordering_same_timestamp():
    dt = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    txs = [
        create_tx(2, TransactionType.BUY, "10", "100", dt=dt), # executed 2nd
        create_tx(1, TransactionType.DEPOSIT, "10000", dt=dt), # executed 1st
    ]
    # Sorting should place DEPOSIT (id=1) before BUY (id=2), allowing the BUY
    state = fold_transactions(txs)
    assert state.cash_balance == Decimal("9000")

def test_negative_quantity_reject():
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "-1000")
    ]
    with pytest.raises(InvalidTransactionError):
        fold_transactions(txs)

def test_float_leakage_decimal_correctness():
    # Exact math checks bypassing floating point errors
    txs = [
        create_tx(1, TransactionType.DEPOSIT, "1000.33"),
        create_tx(2, TransactionType.BUY, "3", "333.11") # 999.33
    ]
    state = fold_transactions(txs)
    assert state.cash_balance == Decimal("1.00")

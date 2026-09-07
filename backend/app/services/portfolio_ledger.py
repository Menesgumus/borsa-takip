from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

@dataclass
class TransactionData:
    id: int
    transaction_type: str
    instrument_id: int | None
    quantity: Decimal
    price: Decimal
    fee: Decimal
    executed_at: Any # datetime

@dataclass
class PositionState:
    instrument_id: int
    quantity: Decimal
    average_cost: Decimal
    realized_pnl: Decimal

@dataclass
class PortfolioState:
    cash_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    positions: dict[int, PositionState]
    total_realized_pnl: Decimal

class InsufficientCashError(Exception):
    pass

class InsufficientPositionError(Exception):
    pass

class InvalidTransactionError(Exception):
    pass

def fold_transactions(transactions: list[TransactionData]) -> PortfolioState:
    # Ensure ordered deterministic
    sorted_txs = sorted(transactions, key=lambda t: (t.executed_at, t.id))

    state = PortfolioState(
        cash_balance=Decimal("0"),
        total_deposits=Decimal("0"),
        total_withdrawals=Decimal("0"),
        positions={},
        total_realized_pnl=Decimal("0")
    )

    for tx in sorted_txs:
        if tx.transaction_type in [TransactionType.BUY, TransactionType.SELL] and tx.quantity <= 0:
            raise InvalidTransactionError(f"Quantity must be positive for {tx.transaction_type}")
        if tx.transaction_type in [TransactionType.DEPOSIT, TransactionType.WITHDRAWAL] and tx.quantity <= 0:
            # Actually, the user spec says amount > 0 for DEPOSIT/WITHDRAWAL. We use quantity field as amount.
            raise InvalidTransactionError(f"Amount must be positive for {tx.transaction_type}")

        if tx.fee < 0:
            raise InvalidTransactionError("Fee cannot be negative")

        if tx.transaction_type == TransactionType.DEPOSIT:
            state.cash_balance += tx.quantity
            state.total_deposits += tx.quantity

        elif tx.transaction_type == TransactionType.WITHDRAWAL:
            if state.cash_balance < tx.quantity:
                raise InsufficientCashError("Insufficient cash for withdrawal")
            state.cash_balance -= tx.quantity
            state.total_withdrawals += tx.quantity

        elif tx.transaction_type == TransactionType.BUY:
            if tx.instrument_id is None:
                raise InvalidTransactionError("BUY must have an instrument_id")

            total_cost = (tx.quantity * tx.price) + tx.fee
            if state.cash_balance < total_cost:
                raise InsufficientCashError("Insufficient cash for BUY")

            state.cash_balance -= total_cost

            pos = state.positions.get(tx.instrument_id)
            if not pos:
                pos = PositionState(
                    instrument_id=tx.instrument_id,
                    quantity=tx.quantity,
                    average_cost=(total_cost / tx.quantity),
                    realized_pnl=Decimal("0")
                )
            else:
                prev_cost_basis = pos.quantity * pos.average_cost
                new_quantity = pos.quantity + tx.quantity
                pos.average_cost = (prev_cost_basis + total_cost) / new_quantity
                pos.quantity = new_quantity
            state.positions[tx.instrument_id] = pos

        elif tx.transaction_type == TransactionType.SELL:
            if tx.instrument_id is None:
                raise InvalidTransactionError("SELL must have an instrument_id")

            pos = state.positions.get(tx.instrument_id)
            if not pos or pos.quantity < tx.quantity:
                raise InsufficientPositionError("SELL quantity exceeds current position")

            gross_proceeds = tx.quantity * tx.price
            net_proceeds = gross_proceeds - tx.fee

            # PNL = proceeds - cost basis of sold amount
            disposed_cost_basis = tx.quantity * pos.average_cost
            realized_pnl = net_proceeds - disposed_cost_basis

            pos.realized_pnl += realized_pnl
            state.total_realized_pnl += realized_pnl

            state.cash_balance += net_proceeds
            pos.quantity -= tx.quantity

            if pos.quantity == Decimal("0"):
                pos.average_cost = Decimal("0")

            # If quantity is 0, we can choose to keep the position object to record realized PNL
            # User said "average_cost output: null veya zero representation. Eski average cost taşınmamalı"
            # Setting it to 0 satisfies this.

    return state

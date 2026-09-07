from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BacktestJobCreate(BaseModel):
    strategy_name: str
    strategy_version: str
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal
    commission_pct: Decimal = Decimal('0.001')
    slippage_pct: Decimal = Decimal('0.0005')

class BacktestJobRead(BacktestJobCreate):
    id: int
    user_id: int
    status: str
    failure_reason: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

class BacktestTradeRead(BaseModel):
    id: int
    instrument_symbol: str
    direction: str
    executed_at: datetime
    quantity: Decimal
    price: Decimal
    fees: Decimal
    slippage: Decimal

class BacktestResultRead(BaseModel):
    id: int
    job_id: int
    total_return_pct: Decimal | None = None
    cagr_pct: Decimal | None = None
    max_drawdown_pct: Decimal | None = None
    win_rate_pct: Decimal | None = None
    total_trades: int | None = None
    fees_paid: Decimal | None = None
    benchmark_return_pct: Decimal | None = None
    equity_curve: str | None = None
    bias_audit: str | None = None
    limitations: str | None = None
    validation_state: str | None = None

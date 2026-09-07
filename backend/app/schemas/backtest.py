from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

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
    failure_reason: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

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
    total_return_pct: Optional[Decimal] = None
    cagr_pct: Optional[Decimal] = None
    max_drawdown_pct: Optional[Decimal] = None
    win_rate_pct: Optional[Decimal] = None
    total_trades: Optional[int] = None
    fees_paid: Optional[Decimal] = None
    benchmark_return_pct: Optional[Decimal] = None
    equity_curve: Optional[str] = None
    bias_audit: Optional[str] = None
    limitations: Optional[str] = None
    validation_state: Optional[str] = None

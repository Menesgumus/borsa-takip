from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.db.models import LifecycleAction, LifecycleHealthState


class LifecycleEvidence(BaseModel):
    market_view: str | None = None
    reason_codes: list[str] = []

class PositionLifecycleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    instrument_id: int
    episode_number: int

    health_state: LifecycleHealthState
    recommended_action: LifecycleAction
    policy_version: str

    negative_confirmation_count: int
    strong_sell_confirmation_count: int
    recovery_confirmation_count: int
    add_confirmation_count: int

    last_counted_market_observation_key: str | None
    last_evaluated_at: datetime | None
    last_transition_at: datetime | None

    episode_started_at: datetime
    closed_at: datetime | None

    # Portfolio Context (derived dynamically when returned)
    symbol: str | None = None
    asset_class: str | None = None
    native_currency: str | None = None

    is_evaluable: bool | None = None
    data_state: str | None = None

    current_quantity: Decimal | None = None
    average_cost_base: Decimal | None = None
    current_market_value_base: Decimal | None = None
    unrealized_pnl_base: Decimal | None = None
    unrealized_pnl_pct: Decimal | None = None
    current_weight: Decimal | None = None

    market_score: Decimal | None = None
    technical_score: Decimal | None = None
    fundamental_score: Decimal | None = None
    data_quality_score: Decimal | None = None

    suggested_reduce_quantity: Decimal | None = None
    suggested_remaining_quantity: Decimal | None = None
    estimated_released_cash_base: Decimal | None = None

    evidence: LifecycleEvidence | None = None

class LifecycleSnapshotDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    episode_number: int
    health_state_before: LifecycleHealthState | None
    health_state_after: LifecycleHealthState
    recommended_action: LifecycleAction
    evaluated_at: datetime

    market_view: str | None
    reason_codes: str | None

class LifecycleSummaryDTO(BaseModel):
    open_positions_count: int
    stable_count: int
    watch_count: int
    reduce_count: int
    exit_count: int


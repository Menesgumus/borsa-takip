from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

from app.db.models import LifecycleHealthState, LifecycleAction

class LifecycleEvidence(BaseModel):
    market_view: Optional[str] = None
    reason_codes: List[str] = []
    
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
    
    last_counted_market_observation_key: Optional[str]
    last_evaluated_at: Optional[datetime]
    last_transition_at: Optional[datetime]
    
    episode_started_at: datetime
    closed_at: Optional[datetime]
    
    # Portfolio Context (derived dynamically when returned)
    symbol: Optional[str] = None
    asset_class: Optional[str] = None
    native_currency: Optional[str] = None
    
    is_evaluable: Optional[bool] = None
    data_state: Optional[str] = None
    
    current_quantity: Optional[Decimal] = None
    average_cost_base: Optional[Decimal] = None
    current_market_value_base: Optional[Decimal] = None
    unrealized_pnl_base: Optional[Decimal] = None
    unrealized_pnl_pct: Optional[Decimal] = None
    current_weight: Optional[Decimal] = None
    
    market_score: Optional[Decimal] = None
    technical_score: Optional[Decimal] = None
    fundamental_score: Optional[Decimal] = None
    data_quality_score: Optional[Decimal] = None
    
    suggested_reduce_quantity: Optional[Decimal] = None
    suggested_remaining_quantity: Optional[Decimal] = None
    estimated_released_cash_base: Optional[Decimal] = None
    
    evidence: Optional[LifecycleEvidence] = None

class LifecycleSnapshotDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    episode_number: int
    health_state_before: Optional[LifecycleHealthState]
    health_state_after: LifecycleHealthState
    recommended_action: LifecycleAction
    evaluated_at: datetime
    
    market_view: Optional[str]
    reason_codes: Optional[str]
    
class LifecycleSummaryDTO(BaseModel):
    open_positions_count: int
    stable_count: int
    watch_count: int
    reduce_count: int
    exit_count: int


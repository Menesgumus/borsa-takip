from pydantic import BaseModel
from typing import Optional, Any, Dict
from decimal import Decimal
from datetime import datetime

class AlertRuleCreate(BaseModel):
    alert_type: str
    instrument_id: Optional[int] = None
    portfolio_id: Optional[int] = None
    operator: Optional[str] = None
    threshold: Optional[Decimal] = None
    config_data: Optional[str] = None
    is_enabled: bool = True
    cooldown_minutes: int = 60

class AlertRuleRead(AlertRuleCreate):
    id: int
    last_triggered_at: Optional[datetime] = None

class NotificationRead(BaseModel):
    id: int
    alert_type: str
    title: str
    message: str
    trigger_data: Optional[str] = None
    is_read: bool
    created_at: datetime

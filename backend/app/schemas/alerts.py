from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AlertRuleCreate(BaseModel):
    alert_type: str
    instrument_id: int | None = None
    portfolio_id: int | None = None
    operator: str | None = None
    threshold: Decimal | None = None
    config_data: str | None = None
    is_enabled: bool = True
    cooldown_minutes: int = 60

class AlertRuleRead(AlertRuleCreate):
    id: int
    last_triggered_at: datetime | None = None

class NotificationRead(BaseModel):
    id: int
    alert_type: str
    title: str
    message: str
    trigger_data: str | None = None
    is_read: bool
    created_at: datetime

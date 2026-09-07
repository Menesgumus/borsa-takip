from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
import json
import logging

from app.db.models import AlertRule, UserNotification

logger = logging.getLogger(__name__)

async def evaluate_alert(db: AsyncSession, rule: AlertRule, current_value: float, context_data: dict) -> bool:
    """
    Evaluates an alert rule. Returns True if a notification was triggered, False otherwise.
    Handles cooldown logic natively.
    """
    if not rule.is_enabled:
        return False
        
    # Cooldown check
    now = datetime.now(timezone.utc)
    if rule.last_triggered_at:
        # DB timezone awareness is crucial, assume UTC
        cooldown_expiry = rule.last_triggered_at.replace(tzinfo=timezone.utc) + timedelta(minutes=rule.cooldown_minutes)
        if now < cooldown_expiry:
            return False # Still in cooldown
            
    is_triggered = False
    
    if rule.operator == ">" and rule.threshold is not None:
        if current_value > float(rule.threshold):
            is_triggered = True
    elif rule.operator == "<" and rule.threshold is not None:
        if current_value < float(rule.threshold):
            is_triggered = True
    elif rule.operator == "==" and rule.threshold is not None:
        if current_value == float(rule.threshold):
            is_triggered = True
    elif rule.operator == "EVENT": # For KAP/News where current_value is just a signal
        is_triggered = True
        
    if is_triggered:
        # Create notification
        notif = UserNotification(
            user_id=rule.user_id,
            rule_id=rule.id,
            alert_type=rule.alert_type,
            title=f"Kural Tetiklendi: {rule.alert_type.value}",
            message=context_data.get("message", "Belirlediğiniz bir kural gerçekleşti."),
            trigger_data=json.dumps(context_data)
        )
        db.add(notif)
        
        # Update rule cooldown timestamp
        rule.last_triggered_at = now
        await db.commit()
        return True
        
    return False

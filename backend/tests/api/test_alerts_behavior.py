import random
import pytest
from decimal import Decimal
import uuid
import datetime

from app.services.alerts import evaluate_alert
from app.db.models import AlertRule, AlertType, UserNotification, User
from app.db.session import async_session_maker

@pytest.mark.asyncio
async def test_alert_price_threshold():
    async with async_session_maker() as db:
        user = User(id=random.randint(1000000, 9999999), email=f"x_{uuid.uuid4()}@a.com", password_hash="1")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        rule = AlertRule(user_id=user.id, alert_type=AlertType.PRICE, operator=">", threshold=Decimal("100"), cooldown_minutes=60, is_enabled=True)
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        
        # 90 is not > 100
        assert await evaluate_alert(db, rule, 90.0, {}) is False
        
        # 110 is > 100 -> True
        assert await evaluate_alert(db, rule, 110.0, {}) is True
        
        # 120 is > 100 but cooldown
        await db.refresh(rule)
        assert await evaluate_alert(db, rule, 120.0, {}) is False

@pytest.mark.asyncio
async def test_alert_disabled_rule():
    async with async_session_maker() as db:
        rule = AlertRule(user_id=1, alert_type=AlertType.PRICE, operator=">", threshold=Decimal("100"), is_enabled=False)
        assert await evaluate_alert(db, rule, 150.0, {}) is False

@pytest.mark.asyncio
async def test_alert_cooldown_expiry():
    async with async_session_maker() as db:
        user = User(id=random.randint(1000000, 9999999), email=f"y_{uuid.uuid4()}@a.com", password_hash="1")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Triggered 2 hours ago
        past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
        rule = AlertRule(user_id=user.id, alert_type=AlertType.RSI, operator="<", threshold=Decimal("30"), cooldown_minutes=60, is_enabled=True, last_triggered_at=past_time)
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        
        # Should trigger because 120 mins > 60 mins cooldown
        assert await evaluate_alert(db, rule, 25.0, {}) is True


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import AlertRule, AlertType, User, UserNotification
from app.db.session import get_db_session
from app.schemas.alerts import AlertRuleCreate, AlertRuleRead, NotificationRead

router = APIRouter()

@router.get("/rules", response_model=list[AlertRuleRead])
async def get_rules(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(AlertRule).where(AlertRule.user_id == current_user.id))
    return res.scalars().all()

@router.post("/rules", response_model=AlertRuleRead)
async def create_rule(data: AlertRuleCreate, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    try:
        atype = AlertType(data.alert_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert_type")

    rule = AlertRule(
        user_id=current_user.id,
        alert_type=atype,
        instrument_id=data.instrument_id,
        portfolio_id=data.portfolio_id,
        operator=data.operator,
        threshold=data.threshold,
        config_data=data.config_data,
        is_enabled=data.is_enabled,
        cooldown_minutes=data.cooldown_minutes
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.get("/notifications", response_model=list[NotificationRead])
async def get_notifications(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(UserNotification).where(UserNotification.user_id == current_user.id).order_by(UserNotification.created_at.desc()))
    return res.scalars().all()

@router.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: int, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(UserNotification).where(UserNotification.id == notif_id, UserNotification.user_id == current_user.id))
    notif = res.scalars().first()
    if not notif:
        raise HTTPException(status_code=404)
    notif.is_read = True
    await db.commit()
    return {"status": "ok"}

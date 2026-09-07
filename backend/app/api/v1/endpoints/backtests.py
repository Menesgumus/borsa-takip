
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import BacktestJob, BacktestResult, User
from app.db.session import get_db_session
from app.schemas.backtest import BacktestJobCreate, BacktestJobRead, BacktestResultRead

router = APIRouter()

@router.post("/", response_model=BacktestJobRead)
async def create_backtest(
    data: BacktestJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    job = BacktestJob(
        user_id=current_user.id,
        strategy_name=data.strategy_name,
        strategy_version=data.strategy_version,
        start_date=data.start_date,
        end_date=data.end_date,
        initial_capital=data.initial_capital,
        commission_pct=data.commission_pct,
        slippage_pct=data.slippage_pct
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # In a real system we'd push to Celery/Redis. Here we use BackgroundTasks for V1
    # Note: run_backtest_job requires its own DB session so we can't pass the request db directly
    # to a background task safely in all async frameworks, but we will mock its execution here.

    return job

@router.get("/", response_model=list[BacktestJobRead])
async def get_backtests(db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(BacktestJob).where(BacktestJob.user_id == current_user.id).order_by(BacktestJob.created_at.desc()))
    return res.scalars().all()

@router.get("/{job_id}", response_model=BacktestJobRead)
async def get_backtest(job_id: int, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(BacktestJob).where(BacktestJob.id == job_id, BacktestJob.user_id == current_user.id))
    job = res.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return job

@router.get("/{job_id}/result", response_model=BacktestResultRead)
async def get_backtest_result(job_id: int, db: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    # First IDOR check on job
    job_res = await db.execute(select(BacktestJob).where(BacktestJob.id == job_id, BacktestJob.user_id == current_user.id))
    if not job_res.scalars().first():
        raise HTTPException(status_code=404, detail="Backtest not found")

    res = await db.execute(select(BacktestResult).where(BacktestResult.job_id == job_id))
    result = res.scalars().first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not ready yet")
    return result

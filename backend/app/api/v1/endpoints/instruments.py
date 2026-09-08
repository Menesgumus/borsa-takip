from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, OHLCVDaily, User
from app.db.session import get_db_session
from app.market.dto import QuoteDTO
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.schemas.decision import (
    DecisionResult,
    FundamentalInputs,
    Horizon,
    NewsInputs,
    PortfolioFitInputs,
    TechnicalInputs,
)
from app.schemas.instrument import InstrumentResponse, InstrumentsPaginated, OHLCVDailyResponse
from app.schemas.technical import TechnicalAnalysisResponse
from app.services.decision_engine import evaluate_decision
from app.services.technical_data import get_technical_analysis

router = APIRouter()


@router.get("", response_model=InstrumentsPaginated)
async def list_instruments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """List and search instruments (read-only, public data)."""
    import json
    from app.core.redis import redis_client
    
    cache_key = f"instruments:paginated:{page}:{size}:{search or ''}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        from fastapi.responses import Response
        return Response(content=cached_data, media_type="application/json")

    offset = (page - 1) * size

    stmt = select(Instrument).where(Instrument.is_active.is_(True))
    if search:
        search_term = f"%{search.upper()}%"
        stmt = stmt.where(
            (func.upper(Instrument.symbol).like(search_term))
            | (func.upper(Instrument.name).like(search_term))
        )

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Get items
    stmt = stmt.order_by(Instrument.symbol).limit(size).offset(offset)
    result = await db.execute(stmt)
    items = result.scalars().all()

    from app.schemas.instrument import InstrumentsPaginated
    response_data = InstrumentsPaginated(
        items=items,
        total=total,
        page=page,
        size=size
    )
    
    await redis_client.set(cache_key, response_data.model_dump_json(), ex=60)
    return response_data


@router.get("/{symbol}", response_model=InstrumentResponse)
async def get_instrument(
    symbol: str,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """Get single instrument details."""
    result = await db.execute(
        select(Instrument).where(Instrument.symbol == symbol, Instrument.is_active.is_(True))
    )
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found",
        )
    return instrument


@router.get("/{symbol}/quote", response_model=QuoteDTO)
async def get_instrument_quote(
    symbol: str,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """Get live quote for instrument via provider abstraction."""
    # 1. Resolve instrument
    result = await db.execute(
        select(Instrument)
        .options(selectinload(Instrument.provider_mappings))
        .where(Instrument.symbol == symbol, Instrument.is_active.is_(True))
    )
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found",
        )

    # 2. Get provider mapping (default to "mock" and symbol itself if none)
    provider_name = "mock"
    provider_symbol = str(instrument.symbol)

    if instrument.provider_mappings:
        # Pick primary or first
        mapping = next(
            (m for m in instrument.provider_mappings if m.is_primary),
            instrument.provider_mappings[0],
        )
        provider_name = mapping.provider_name
        provider_symbol = str(mapping.provider_symbol)

    # 3. Fetch quote via registry
    try:
        quote = await registry.get_quote(provider_name, provider_symbol)
        return quote
    except ProviderUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e


@router.get("/{symbol}/history", response_model=list[OHLCVDailyResponse])
async def get_instrument_history(
    symbol: str,
    period: str | None = Query(None, description="E.g., 1M, 3M, 6M, 1Y"),
    start_date: datetime | None = Query(None),  # noqa: B008
    end_date: datetime | None = Query(None),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """Get historical OHLCV data from the database."""
    from datetime import timedelta, UTC
    
    if period and not start_date:
        end_date = end_date or datetime.now(UTC)
        if period.upper() == "1M":
            start_date = end_date - timedelta(days=30)
        elif period.upper() == "3M":
            start_date = end_date - timedelta(days=90)
        elif period.upper() == "6M":
            start_date = end_date - timedelta(days=180)
        elif period.upper() == "1Y":
            start_date = end_date - timedelta(days=365)
            
    result = await db.execute(
        select(Instrument).where(Instrument.symbol == symbol, Instrument.is_active.is_(True))
    )
    instrument = result.scalar_one_or_none()
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found",
        )

    stmt = select(OHLCVDaily).where(OHLCVDaily.instrument_id == instrument.id)
    if start_date:
        stmt = stmt.where(OHLCVDaily.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(OHLCVDaily.timestamp <= end_date)

    stmt = stmt.order_by(OHLCVDaily.timestamp.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{symbol}/technical", response_model=TechnicalAnalysisResponse)
async def get_instrument_technical(
    symbol: str,
    start_date: datetime | None = Query(None),  # noqa: B008
    end_date: datetime | None = Query(None),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """Get technical analysis indicators for an instrument."""
    try:
        return await get_technical_analysis(db, symbol, start_date, end_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

from datetime import UTC

from app.market.context_providers.evds_provider import EVDSProvider
from app.market.context_providers.kap_provider import KAPProvider
from app.market.context_providers.mock_news_provider import MockNewsProvider
from app.schemas.context import ContextResponse


@router.get("/{symbol}/context", response_model=ContextResponse)
async def get_instrument_context(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get Fundamentals, KAP, News, and Macro context."""
    from app.core.config import settings
    
    news = []
    if settings.ENABLE_MOCK_MARKET_DATA:
        from app.market.context_providers.mock_news_provider import MockNewsProvider
        news_provider = MockNewsProvider()
        news = await news_provider.get_latest_news(symbol)

    from app.market.context_providers.evds_provider import EVDSProvider
    from app.market.context_providers.kap_provider import KAPProvider
    kap_provider = KAPProvider()
    evds_provider = EVDSProvider()

    disclosures = await kap_provider.get_latest_disclosures(symbol)
    # Example macro: USD/TRY
    macro = await evds_provider.get_macro_series(["TP.DK.USD.S.YTL"])

    availability = {
        "news": await news_provider.is_available() if 'news_provider' in locals() else False,
        "kap": await kap_provider.is_available(),
        "evds": await evds_provider.is_available(),
        "fundamentals": False
    }

    return ContextResponse(
        symbol=symbol,
        fetched_at=datetime.now(UTC),
        freshness="DELAYED" if any(availability.values()) else "STALE",
        availability=availability,
        fundamentals=[],
        disclosures=disclosures,
        news=news,
        macro=macro
    )


@router.get("/{symbol}/decision", response_model=DecisionResult)
async def get_instrument_decision(
    symbol: str,
    horizon: Horizon = Horizon.MEDIUM,
    portfolio_id: int | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Get instrument
    result = await db.execute(select(Instrument).where(Instrument.symbol == symbol))
    instrument = result.scalars().first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # Get Context/Data
    from app.api.v1.endpoints.instruments import get_instrument_context
    context = await get_instrument_context(symbol, db, current_user)

    # 1. Technical Inputs
    try:
        from app.services.technical_data import get_technical_analysis
        tech_response = await get_technical_analysis(db, symbol)
        if not tech_response.indicators:
            tech = TechnicalInputs(current_price=None, rsi_14=None, macd_line=None, macd_signal=None, sma_50=None, sma_200=None)
        else:
            latest = tech_response.indicators[-1]
            tech = TechnicalInputs(
                current_price=Decimal(str(latest.close)) if hasattr(latest, 'close') else Decimal("0"),
                rsi_14=Decimal(str(latest.rsi_14)) if latest.rsi_14 is not None else None,
                macd_line=Decimal(str(latest.macd_line)) if latest.macd_line is not None else None,
                macd_signal=Decimal(str(latest.macd_signal)) if latest.macd_signal is not None else None,
                sma_50=Decimal(str(latest.sma_20)) if latest.sma_20 is not None else None,
                sma_200=Decimal(str(latest.sma_20)) if latest.sma_20 is not None else None
            )
            try:
                quote = await registry.get_quote("yahoo", symbol)
                tech.current_price = quote.price
                tech.is_stale = quote.is_stale
            except Exception:
                pass
    except Exception:
        tech = TechnicalInputs(current_price=None, rsi_14=None, macd_line=None, macd_signal=None, sma_50=None, sma_200=None)

    # 2. Fundamental Inputs
    fund = FundamentalInputs(instrument_type=instrument.instrument_type.value)
    if hasattr(context, 'fundamentals') and context.fundamentals:
        # F/K and PD/DD might be in metrics JSON
        metrics = context.fundamentals.metrics or {}
        fk = metrics.get('f_k') or metrics.get('pe_ratio')
        pddd = metrics.get('pd_dd') or metrics.get('pb_ratio')
        if fk:
            fund.pe_ratio = Decimal(str(fk))
        if pddd:
            fund.pb_ratio = Decimal(str(pddd))

    # 3. News Inputs
    news_input = NewsInputs(is_mock=True) # default mock
    if hasattr(context, 'news') and context.news:
        news_input.news_count = len(context.news)
        news_input.sentiment_score = Decimal("60") # Simplified
        news_input.is_mock = any('mock' in getattr(n, 'source', '').lower() for n in context.news)

    # 4. Portfolio Fit
    pf = None
    if portfolio_id:
        from app.db.models import Portfolio
        p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id))
        p = p_res.scalars().first()
        if p:
            # We would calculate current weight from Ledger.
            pf = PortfolioFitInputs(current_weight=Decimal("10"), max_weight_limit=Decimal("30"))

    # Evaluate
    decision = evaluate_decision(instrument.id, horizon, tech, fund, news_input, pf)

    # Snapshot (Immutability)
    from app.db.models import DecisionSnapshot
    snap = DecisionSnapshot(
        instrument_id=instrument.id,
        action=decision.market_view,
        score=decision.overall_market_score,
        engine_version=decision.engine_version,
        reason_codes=",".join(decision.reason_codes)
    )
    db.add(snap)
    await db.commit()

    return decision

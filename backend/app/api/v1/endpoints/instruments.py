from __future__ import annotations

from datetime import datetime
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
    Horizon,
)
from app.schemas.instrument import (
    BatchQuoteItem,
    BatchQuoteResponse,
    InstrumentResponse,
    InstrumentsPaginated,
    OHLCVDailyResponse,
)
from app.schemas.technical import TechnicalAnalysisResponse
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
    from app.core.redis import redis_client

    cache_key = f"instruments:paginated:{page}:{size}:{search or ''}"
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            from fastapi.responses import Response
            return Response(content=cached_data, media_type="application/json")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Redis cache error: {e}")

    offset = (page - 1) * size

    query = select(Instrument).where(Instrument.is_active == True)  # noqa: E712
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Instrument.symbol.ilike(search_pattern))
            | (Instrument.name.ilike(search_pattern))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get items
    query = query.order_by(Instrument.symbol).limit(size).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    from app.schemas.instrument import InstrumentsPaginated
    response_data = InstrumentsPaginated(
        items=items,
        total=total,
        page=page,
        size=size
    )

    try:
        await redis_client.set(cache_key, response_data.model_dump_json(), ex=60)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Redis cache set error: {e}")

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



@router.get("/quotes/batch", response_model=BatchQuoteResponse)
async def get_instrument_quotes_batch(
    symbols: str = Query(..., description="Comma separated canonical symbols"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Batch quote endpoint.

    DB work is completed and materialized BEFORE any external provider I/O.
    One failed symbol does not fail the whole batch.
    Frozen QuoteDTO is NEVER mutated - model_copy is used for symbol remapping.
    Unavailable quotes are NEVER represented as price=0.
    """
    import asyncio
    from collections import defaultdict
    from datetime import UTC, datetime

    from app.services.provider_resolver import resolve_provider

    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    # ── DB PHASE: complete all DB work before external I/O ──────────────────
    res = await db.execute(
        select(Instrument)
        .options(selectinload(Instrument.provider_mappings))
        .where(Instrument.symbol.in_(symbol_list), Instrument.is_active.is_(True))
    )
    instruments = res.scalars().all()

    # Materialize resolution data before session becomes idle
    found_symbols = {inst.symbol for inst in instruments}
    by_provider: dict[str, list[str]] = defaultdict(list)
    symbol_map: dict[str, str] = {}  # provider_symbol -> canonical_symbol
    items: dict[str, BatchQuoteItem] = {}

    # Mark not-found symbols
    for sym in symbol_list:
        if sym not in found_symbols:
            items[sym] = BatchQuoteItem(symbol=sym, status="NOT_FOUND", error_code="INSTRUMENT_NOT_IN_DB")

    for inst in instruments:
        try:
            resolved = resolve_provider(inst)
            by_provider[resolved.provider_name].append(resolved.provider_symbol)
            symbol_map[resolved.provider_symbol] = inst.symbol
        except ProviderUnavailableError as e:
            sym_str = str(inst.symbol)
            items[sym_str] = BatchQuoteItem(
                symbol=sym_str, status="UNAVAILABLE", error_code=str(e)[:200]
            )

    # ── EXTERNAL I/O PHASE ───────────────────────────────────────────────────
    async def fetch_provider_batch(provider_name: str, provider_symbols: list[str]) -> None:
        try:
            # 12-second hard deadline for the whole provider batch
            quotes = await asyncio.wait_for(
                registry.get_quotes(provider_name, provider_symbols),
                timeout=12.0,
            )
            returned_psymbols = {q.symbol for q in quotes}
            for q in quotes:
                canonical = symbol_map.get(q.symbol, q.symbol)
                # Remap provider symbol to canonical using model_copy (frozen DTO)
                mapped_q = q.model_copy(update={"symbol": canonical})
                items[canonical] = BatchQuoteItem(symbol=canonical, status="AVAILABLE", quote=mapped_q)

            # Provider silently omitted some symbols
            for ps in provider_symbols:
                if ps not in returned_psymbols:
                    canonical = symbol_map.get(ps, ps)
                    if canonical not in items:
                        items[canonical] = BatchQuoteItem(
                            symbol=canonical,
                            status="UNAVAILABLE",
                            error_code="NOT_RETURNED_BY_PROVIDER",
                        )
        except TimeoutError:
            for ps in provider_symbols:
                canonical = symbol_map.get(ps, ps)
                items[canonical] = BatchQuoteItem(
                    symbol=canonical, status="TIMEOUT", error_code="BATCH_DEADLINE_EXCEEDED"
                )
        except Exception as exc:
            for ps in provider_symbols:
                canonical = symbol_map.get(ps, ps)
                items[canonical] = BatchQuoteItem(
                    symbol=canonical, status="PROVIDER_ERROR", error_code=str(exc)[:200]
                )

    if by_provider:
        await asyncio.gather(*[
            fetch_provider_batch(pname, psyms)
            for pname, psyms in by_provider.items()
        ])

    available_count = sum(1 for i in items.values() if i.status == "AVAILABLE")
    return BatchQuoteResponse(
        items=items,
        requested_count=len(symbol_list),
        available_count=available_count,
        unavailable_count=len(items) - available_count,
        as_of=datetime.now(UTC),
    )

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

    # 2. Resolve provider mapping using canonical resolver
    from app.services.provider_resolver import resolve_provider
    try:
        resolved = resolve_provider(instrument)
        provider_name = resolved.provider_name
        provider_symbol = resolved.provider_symbol
    except ProviderUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No provider configured for instrument '{symbol}'",
        )

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
    from datetime import UTC, timedelta

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
        elif period.upper() == "2Y":
            start_date = end_date - timedelta(days=730)

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
    # Get instrument with provider_mappings loaded
    result = await db.execute(
        select(Instrument)
        .options(selectinload(Instrument.provider_mappings))
        .where(Instrument.symbol == symbol)
    )
    instrument = result.scalars().first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    from app.services.decision_engine import resolve_and_evaluate_decision
    return await resolve_and_evaluate_decision(instrument, symbol, db, current_user, horizon, portfolio_id)

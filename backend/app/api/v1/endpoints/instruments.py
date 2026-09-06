from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import Instrument, User
from app.db.session import get_db_session
from app.market.dto import QuoteDTO
from app.market.exceptions import ProviderUnavailableError
from app.market.mock_provider import MockMarketDataProvider
from app.market.registry import registry
from app.schemas.instrument import InstrumentResponse, InstrumentsPaginated

router = APIRouter()

# Register mock provider at startup
mock_provider = MockMarketDataProvider()
registry.register(mock_provider, is_primary=True)


@router.get("", response_model=InstrumentsPaginated)
async def list_instruments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> Any:
    """List and search instruments (read-only, public data)."""
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

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }


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

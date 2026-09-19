import logging
import json
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client
from app.db.models import AssetClass, Instrument
from app.market.registry import MarketDataRegistry
from app.services.provider_resolver import resolve_provider

logger = logging.getLogger(__name__)

CACHE_TTL = 900  # 15 minutes


@dataclass
class FxRateResult:
    rate: Decimal
    source: str
    as_of: datetime
    data_state: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rate": str(self.rate),
            "source": self.source,
            "as_of": self.as_of.isoformat(),
            "data_state": self.data_state
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FxRateResult":
        return cls(
            rate=Decimal(data["rate"]),
            source=data["source"],
            as_of=datetime.fromisoformat(data["as_of"]),
            data_state=data["data_state"]
        )


class FxRateService:
    def __init__(self, registry: MarketDataRegistry) -> None:
        self.registry = registry

    async def get_usd_try_rate(self, db_session: AsyncSession) -> FxRateResult | None:
        redis_gen = get_redis_client()
        redis = None
        try:
            redis = await anext(redis_gen)
            if hasattr(redis, 'get'):
                cached = await redis.get("fx:usdtry_result")
                if cached is not None:
                    if isinstance(cached, bytes):
                        cached = cached.decode('utf-8')
                    data = json.loads(cached)
                    return FxRateResult.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to read FX from cache: {e}")

        # If not in cache, fetch from provider
        try:
            result = await db_session.execute(
                select(Instrument)
                .options(selectinload(Instrument.provider_mappings))
                .where(
                    Instrument.asset_class == AssetClass.FX_REFERENCE,
                    Instrument.symbol.in_(["USDTRY=X", "QAUSDTRY"])
                )
            )
            instruments = result.scalars().all()

            # Prefer QAUSDTRY in test environment if it exists
            instrument = next((i for i in instruments if i.symbol == "QAUSDTRY"), None)
            if not instrument:
                instrument = next((i for i in instruments if i.symbol == "USDTRY=X"), None)

            if not instrument:
                logger.error("No USDTRY FX reference instrument found in database.")
                return None

            resolved = resolve_provider(instrument)
            quote = await self.registry.get_quote(resolved.provider_name, resolved.provider_symbol)
            if not quote:
                logger.error("Failed to get quote for USDTRY FX reference.")
                return None

            fx_result = FxRateResult(
                rate=quote.price,
                source=resolved.provider_name,
                as_of=quote.timestamp,
                data_state=quote.data_state
            )

            try:
                if redis and hasattr(redis, 'setex'):
                    await redis.setex("fx:usdtry_result", CACHE_TTL, json.dumps(fx_result.to_dict()))
            except Exception as e:
                logger.warning(f"Failed to write FX to cache: {e}")

            return fx_result
        except Exception as e:
            logger.error(f"Error fetching USDTRY rate: {e}")
            import traceback
            traceback.print_exc()
            return None

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client
from app.db.models import AssetClass, Instrument
from app.market.registry import MarketDataRegistry

logger = logging.getLogger(__name__)

CACHE_TTL = 900  # 15 minutes


class FxRateService:
    def __init__(self, registry: MarketDataRegistry) -> None:
        self.registry = registry

    async def get_usd_try_rate(self, db_session: AsyncSession) -> Decimal | None:
        # First, try to get from redis
        try:
            redis_gen = get_redis_client()
            redis = await anext(redis_gen)
            if hasattr(redis, 'get'):
                cached = await redis.get("fx:usdtry")
                if cached is not None:
                    if isinstance(cached, bytes):
                        cached = cached.decode('utf-8')
                    return Decimal(str(cached))
        except Exception as e:
            logger.warning(f"Failed to read FX from cache: {e}")

        # If not in cache, fetch from provider
        try:
            result = await db_session.execute(
                select(Instrument).where(
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

            quote = await self.registry.get_quote(instrument.symbol, instrument)
            if not quote:
                logger.error("Failed to get quote for USDTRY FX reference.")
                return None

            rate = quote.price

            try:
                if hasattr(redis, 'setex'):
                    await redis.setex("fx:usdtry", CACHE_TTL, str(rate))
            except Exception as e:
                logger.warning(f"Failed to write FX to cache: {e}")

            return rate
        except Exception as e:
            logger.error(f"Error fetching USDTRY rate: {e}")
            import traceback
            traceback.print_exc()
            return None

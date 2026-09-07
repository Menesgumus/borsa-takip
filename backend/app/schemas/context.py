from datetime import datetime

from pydantic import BaseModel

from app.market.context_providers.base import DisclosureDTO, FundamentalDTO, MacroDTO, NewsDTO


class ContextResponse(BaseModel):
    symbol: str
    fetched_at: datetime
    freshness: str
    availability: dict[str, bool]

    fundamentals: list[FundamentalDTO] = []
    disclosures: list[DisclosureDTO] = []
    news: list[NewsDTO] = []
    macro: list[MacroDTO] = []

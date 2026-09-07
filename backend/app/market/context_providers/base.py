from datetime import datetime

from pydantic import BaseModel


class DisclosureDTO(BaseModel):
    index: str
    title: str
    content: str
    published_at: datetime
    category: str | None = None

class NewsDTO(BaseModel):
    source_id: str
    provider_name: str
    title: str
    summary: str
    published_at: datetime
    url: str | None = None
    is_synthetic: bool = False

class FundamentalDTO(BaseModel):
    period: str
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    market_cap: float | None = None
    net_income: float | None = None
    revenue: float | None = None
    published_at: datetime

class MacroDTO(BaseModel):
    series_code: str
    value: float
    timestamp: datetime
    description: str

class ContextProviderBase:
    async def is_available(self) -> bool:
        return True

class KAPProviderBase(ContextProviderBase):
    async def get_latest_disclosures(self, symbol: str, limit: int = 5) -> list[DisclosureDTO]:
        raise NotImplementedError

class NewsProviderBase(ContextProviderBase):
    async def get_latest_news(self, symbol: str, limit: int = 5) -> list[NewsDTO]:
        raise NotImplementedError

class FundamentalProviderBase(ContextProviderBase):
    async def get_fundamentals(self, symbol: str) -> list[FundamentalDTO]:
        raise NotImplementedError

class MacroProviderBase(ContextProviderBase):
    async def get_macro_series(self, series_codes: list[str]) -> list[MacroDTO]:
        raise NotImplementedError

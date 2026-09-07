from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class DisclosureDTO(BaseModel):
    index: str
    title: str
    content: str
    published_at: datetime
    category: Optional[str] = None

class NewsDTO(BaseModel):
    source_id: str
    provider_name: str
    title: str
    summary: str
    published_at: datetime
    url: Optional[str] = None
    is_synthetic: bool = False

class FundamentalDTO(BaseModel):
    period: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    net_income: Optional[float] = None
    revenue: Optional[float] = None
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
    async def get_latest_disclosures(self, symbol: str, limit: int = 5) -> List[DisclosureDTO]:
        raise NotImplementedError

class NewsProviderBase(ContextProviderBase):
    async def get_latest_news(self, symbol: str, limit: int = 5) -> List[NewsDTO]:
        raise NotImplementedError

class FundamentalProviderBase(ContextProviderBase):
    async def get_fundamentals(self, symbol: str) -> List[FundamentalDTO]:
        raise NotImplementedError

class MacroProviderBase(ContextProviderBase):
    async def get_macro_series(self, series_codes: List[str]) -> List[MacroDTO]:
        raise NotImplementedError

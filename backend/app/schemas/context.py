from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.market.context_providers.base import DisclosureDTO, NewsDTO, FundamentalDTO, MacroDTO

class ContextResponse(BaseModel):
    symbol: str
    fetched_at: datetime
    freshness: str
    availability: dict[str, bool]
    
    fundamentals: List[FundamentalDTO] = []
    disclosures: List[DisclosureDTO] = []
    news: List[NewsDTO] = []
    macro: List[MacroDTO] = []

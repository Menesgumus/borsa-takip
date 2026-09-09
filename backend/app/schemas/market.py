
from pydantic import BaseModel

from app.market.dto import QuoteDTO


class BatchQuoteRequest(BaseModel):
    symbols: list[str]

class BatchQuoteResponse(BaseModel):
    quotes: dict[str, QuoteDTO]

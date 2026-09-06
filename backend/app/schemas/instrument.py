from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstrumentBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    instrument_type: str
    is_active: bool = True


class InstrumentResponse(InstrumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstrumentsPaginated(BaseModel):
    items: list[InstrumentResponse]
    total: int
    page: int
    size: int

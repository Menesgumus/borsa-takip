from datetime import datetime

from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    content: str
    instrument_symbol: str | None = None
    explanation_level: str = "PRO" # BEGINNER, INTERMEDIATE, PRO

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class ChatThreadResponse(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    messages: list[ChatMessageResponse] = []

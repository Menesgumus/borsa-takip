from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageCreate(BaseModel):
    content: str
    instrument_symbol: Optional[str] = None
    explanation_level: str = "PRO" # BEGINNER, INTERMEDIATE, PRO

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

class ChatThreadResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    messages: List[ChatMessageResponse] = []

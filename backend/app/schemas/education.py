from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LessonRead(BaseModel):
    id: int
    slug: str
    title: str
    summary: Optional[str] = None
    content_beginner: str
    content_detailed: str
    key_points: Optional[str] = None
    related_terms: Optional[str] = None
    display_order: int
    estimated_minutes: int
    is_completed: bool = False

class ModuleRead(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    category: str
    display_order: int
    lessons: List[LessonRead] = []

class ProgressUpdate(BaseModel):
    is_completed: bool
    last_position: Optional[str] = None


from pydantic import BaseModel


class LessonRead(BaseModel):
    id: int
    slug: str
    title: str
    summary: str | None = None
    content_beginner: str
    content_detailed: str
    key_points: str | None = None
    related_terms: str | None = None
    display_order: int
    estimated_minutes: int
    is_completed: bool = False

class ModuleRead(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    category: str
    display_order: int
    lessons: list[LessonRead] = []

class ProgressUpdate(BaseModel):
    is_completed: bool
    last_position: str | None = None

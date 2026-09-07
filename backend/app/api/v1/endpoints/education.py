from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db_session
from app.api.v1.endpoints.auth import get_current_user
from app.db.models import User, EducationalModule, EducationalLesson, UserLessonProgress
from app.schemas.education import ModuleRead, LessonRead, ProgressUpdate

router = APIRouter()

@router.get("/modules", response_model=List[ModuleRead])
async def get_modules(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Fetch modules
    res_mod = await db.execute(select(EducationalModule).where(EducationalModule.is_active == True).order_by(EducationalModule.display_order))
    modules = res_mod.scalars().all()
    
    # Fetch lessons
    res_les = await db.execute(select(EducationalLesson).where(EducationalLesson.is_published == True).order_by(EducationalLesson.display_order))
    lessons = res_les.scalars().all()
    
    # Fetch progress
    res_prog = await db.execute(select(UserLessonProgress).where(UserLessonProgress.user_id == current_user.id))
    progresses = res_prog.scalars().all()
    completed_ids = {p.lesson_id for p in progresses if p.is_completed}
    
    mod_dict = {}
    for m in modules:
        mod_dict[m.id] = ModuleRead(
            id=m.id, slug=m.slug, title=m.title, description=m.description, 
            category=m.category, display_order=m.display_order, lessons=[]
        )
        
    for l in lessons:
        if l.module_id in mod_dict:
            lr = LessonRead(
                id=l.id, slug=l.slug, title=l.title, summary=l.summary,
                content_beginner=l.content_beginner, content_detailed=l.content_detailed,
                key_points=l.key_points, related_terms=l.related_terms,
                display_order=l.display_order, estimated_minutes=l.estimated_minutes,
                is_completed=(l.id in completed_ids)
            )
            mod_dict[l.module_id].lessons.append(lr)
            
    return list(mod_dict.values())

@router.put("/lessons/{lesson_id}/progress")
async def update_progress(
    lesson_id: int,
    data: ProgressUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(UserLessonProgress).where(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ))
    progress = res.scalars().first()
    
    from sqlalchemy.sql import func
    
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            is_completed=data.is_completed,
            last_position=data.last_position,
            completed_at=func.now() if data.is_completed else None
        )
        db.add(progress)
    else:
        progress.is_completed = data.is_completed
        progress.last_position = data.last_position
        if data.is_completed and not progress.completed_at:
            progress.completed_at = func.now()
            
    await db.commit()
    return {"status": "ok"}

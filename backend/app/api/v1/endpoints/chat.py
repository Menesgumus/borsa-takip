from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import ChatMessage, ChatThread, DecisionSnapshot, Instrument, User
from app.db.session import get_db_session
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatThreadResponse
from app.services.ai_orchestrator import MentorContext, generate_mentor_response

router = APIRouter()

@router.post("/threads", response_model=ChatThreadResponse)
async def create_thread(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    thread = ChatThread(user_id=current_user.id, title="Yeni Sohbet")
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return ChatThreadResponse(id=thread.id, title=thread.title, created_at=thread.created_at, messages=[])

@router.get("/threads/{thread_id}", response_model=ChatThreadResponse)
async def get_thread(
    thread_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # IDOR protection
    res = await db.execute(select(ChatThread).where(ChatThread.id == thread_id, ChatThread.user_id == current_user.id))
    thread = res.scalars().first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    m_res = await db.execute(select(ChatMessage).where(ChatMessage.thread_id == thread.id).order_by(ChatMessage.created_at.asc()))
    messages = m_res.scalars().all()

    return ChatThreadResponse(
        id=thread.id,
        title=thread.title,
        created_at=thread.created_at,
        messages=[ChatMessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in messages]
    )

@router.post("/threads/{thread_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    thread_id: int,
    message: ChatMessageCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Verify thread (IDOR check)
    res = await db.execute(select(ChatThread).where(ChatThread.id == thread_id, ChatThread.user_id == current_user.id))
    thread = res.scalars().first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Save user message
    user_msg = ChatMessage(thread_id=thread.id, role="user", content=message.content)
    db.add(user_msg)

    # Assembly Context
    from app.db.models import DecisionAction
    ctx = MentorContext(
        instrument_symbol=message.instrument_symbol or "GENEL",
        deterministic_action=DecisionAction.HOLD,
        deterministic_score=Decimal("0"),
        reason_codes=["NO_CONTEXT"],
        missing_data=True
    )

    if message.instrument_symbol:
        i_res = await db.execute(select(Instrument).where(Instrument.symbol == message.instrument_symbol))
        inst = i_res.scalars().first()
        if inst:
            # Latest Decision Snapshot
            d_res = await db.execute(
                select(DecisionSnapshot)
                .where(DecisionSnapshot.instrument_id == inst.id)
                .order_by(DecisionSnapshot.calculated_at.desc())
                .limit(1)
            )
            decision = d_res.scalars().first()
            if decision:
                ctx.deterministic_action = decision.action
                ctx.deterministic_score = decision.score
                ctx.reason_codes = decision.reason_codes.split(',') if decision.reason_codes else []
                ctx.missing_data = "INSUFFICIENT_DATA" in ctx.reason_codes
                # In a real app we'd fetch price from Phase 05 Technical engine
                ctx.current_price = Decimal("100")

    # Generate structured output
    explanation = await generate_mentor_response(
        user_prompt=message.content,
        context=ctx,
        explanation_level=message.explanation_level
    )

    # Store JSON representation so UI can parse Structured Output
    ai_msg = ChatMessage(thread_id=thread.id, role="assistant", content=explanation.model_dump_json())
    db.add(ai_msg)

    await db.commit()
    await db.refresh(ai_msg)

    return ChatMessageResponse(id=ai_msg.id, role=ai_msg.role, content=ai_msg.content, created_at=ai_msg.created_at)

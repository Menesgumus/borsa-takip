import re
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.models import ChatMessage, ChatThread, DecisionSnapshot, Instrument, OHLCVDaily, User
from app.db.session import get_db_session
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatThreadResponse
from app.services.ai_orchestrator import MentorContext, generate_mentor_response

router = APIRouter()

# Matches 4-5 uppercase ASCII letters that look like a stock ticker
_TICKER_RE = re.compile(r'\b([A-Z]{4,5})\b')


async def _recover_thread_symbol(
    thread_id: int,
    db: AsyncSession,
) -> str | None:
    """Scan recent user messages in this thread backwards to find the most recent
    valid instrument symbol. Validates against the Instrument table.
    Returns None if no valid symbol found.
    """
    hist_res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread_id, ChatMessage.role == "user")
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
    )
    user_messages = hist_res.scalars().all()

    for msg in user_messages:
        matches = _TICKER_RE.findall(msg.content)
        for candidate in matches:
            inst_res = await db.execute(
                select(Instrument)
                .where(Instrument.symbol == candidate, Instrument.is_active.is_(True))
            )
            inst = inst_res.scalars().first()
            if inst:
                return candidate

    return None


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

    # Load recent conversation history for multi-turn context (last 20 messages)
    hist_res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
    )
    history = list(reversed(hist_res.scalars().all()))

    # Save user message first (flush only, commit at end)
    user_msg = ChatMessage(thread_id=thread.id, role="user", content=message.content)
    db.add(user_msg)
    await db.flush()

    # Resolve active instrument symbol:
    # Priority 1: explicit message.instrument_symbol
    # Priority 2: recover from recent thread history (backend-side)
    resolved_symbol = message.instrument_symbol
    if not resolved_symbol:
        resolved_symbol = await _recover_thread_symbol(thread_id, db)

    # Build initial context (default: general question with no instrument data)
    from app.db.models import DecisionAction
    ctx = MentorContext(
        instrument_symbol=resolved_symbol or "GENEL",
        deterministic_action=DecisionAction.HOLD,
        deterministic_score=Decimal("0"),
        reason_codes=["NO_CONTEXT"],
        missing_data=True
    )

    if resolved_symbol:
        i_res = await db.execute(
            select(Instrument)
            .options(selectinload(Instrument.provider_mappings))
            .where(Instrument.symbol == resolved_symbol, Instrument.is_active.is_(True))
        )
        inst = i_res.scalars().first()
        if inst:
            # Load latest Decision Snapshot
            d_res = await db.execute(
                select(DecisionSnapshot)
                .where(DecisionSnapshot.instrument_id == inst.id)
                .order_by(DecisionSnapshot.calculated_at.desc())
                .limit(1)
            )
            decision = d_res.scalars().first()

            if not decision:
                # If no snapshot exists, calculate it dynamically using the deterministic engine.
                from app.schemas.decision import Horizon
                from app.services.decision_engine import resolve_and_evaluate_decision
                decision_res = await resolve_and_evaluate_decision(inst, inst.symbol, db, current_user, Horizon.MEDIUM, None)
                ctx.deterministic_action = decision_res.market_view
                ctx.deterministic_score = decision_res.overall_market_score
                ctx.reason_codes = decision_res.reason_codes
                ctx.missing_data = "INSUFFICIENT_DATA" in ctx.reason_codes
            else:
                ctx.deterministic_action = decision.action
                ctx.deterministic_score = decision.score
                ctx.reason_codes = decision.reason_codes.split(",") if decision.reason_codes else []
                ctx.missing_data = "INSUFFICIENT_DATA" in ctx.reason_codes

            # Try to get live/delayed quote via canonical provider resolver (NO fake prices)
            try:
                from app.market.registry import registry
                from app.services.provider_resolver import resolve_provider
                resolved = resolve_provider(inst)
                quote = await registry.get_quote(resolved.provider_name, resolved.provider_symbol)
                ctx.current_price = quote.price
            except Exception:
                # Fallback: latest OHLCV close (honest, no fabrication)
                try:
                    ohlcv_res = await db.execute(
                        select(OHLCVDaily)
                        .where(OHLCVDaily.instrument_id == inst.id)
                        .order_by(OHLCVDaily.timestamp.desc())
                        .limit(1)
                    )
                    latest_candle = ohlcv_res.scalars().first()
                    if latest_candle:
                        ctx.current_price = Decimal(str(latest_candle.close))
                except Exception:
                    pass  # current_price remains None — never fabricated

    # Build conversation history for multi-turn LLM context
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in history
    ]

    # Generate structured response
    explanation = await generate_mentor_response(
        user_prompt=message.content,
        context=ctx,
        explanation_level=message.explanation_level,
        conversation_history=conversation_history,
    )

    # Store as JSON for frontend to parse
    ai_msg = ChatMessage(thread_id=thread.id, role="assistant", content=explanation.model_dump_json())
    db.add(ai_msg)

    await db.commit()
    await db.refresh(ai_msg)

    return ChatMessageResponse(id=ai_msg.id, role=ai_msg.role, content=ai_msg.content, created_at=ai_msg.created_at)

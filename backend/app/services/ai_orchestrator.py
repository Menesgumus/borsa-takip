import os
from typing import Any

from app.services.ai_mentor import (
    BaseMentorProvider,
    MentorContext,
    MentorExplanation,
    MockMentorProvider,
    OpenAIMentorProvider,
    logger,
)


def get_mentor_provider() -> BaseMentorProvider:
    """Select provider: real OpenAI if key+flag set, else deterministic fallback."""
    if os.getenv("OPENAI_API_KEY") and os.getenv("USE_MOCK_MENTOR", "true").lower() == "false":
        try:
            return OpenAIMentorProvider()
        except Exception as e:
            logger.warning(f"Failed to init OpenAI provider: {e}. Using deterministic fallback.")
            return MockMentorProvider()
    return MockMentorProvider()


async def generate_mentor_response(
    user_prompt: str,
    context: MentorContext,
    explanation_level: str,
    conversation_history: list[dict[str, Any]] | None = None,
) -> MentorExplanation:
    provider = get_mentor_provider()

    try:
        explanation = await provider.generate_explanation(
            user_prompt=user_prompt,
            context=context,
            level=explanation_level,
            conversation_history=conversation_history or [],
        )
    except Exception as e:
        logger.error(f"Mentor provider failed: {e}")
        explanation = MentorExplanation(
            summary="Yapay Zeka asistanina su an ulasilmiyor. Deterministik motor kararini sunuyoruz.",
            action_explanation="Karar motoru skorlarina gore bu sonuc uretilmistir.",
            key_reasons=context.reason_codes,
            risks=["Sistem hatasi - lutfen daha sonra tekrar deneyin."],
            data_quality_note="AI_MENTOR_UNAVAILABLE",
            learning_points=[],
            action=context.deterministic_action.value,
            synthetic=True,
        )

    # ■ FINANCIAL INTEGRITY & ACTION PARITY - HARD INVARIANTS ■
    if explanation.response_kind == "DECISION":
        import re

        def _extract_numbers(text: str) -> set[float]:
            if not text:
                return set()
            matches = re.findall(r'\d+(?:\.\d+)?', text.replace(',', '.'))
            return {float(m) for m in matches}

        authoritative = set()
        if context.current_price is not None:
            authoritative.add(float(context.current_price))
        if context.deterministic_score is not None:
            authoritative.add(float(context.deterministic_score))
        for reason in context.reason_codes:
            matches = re.findall(r'\d+(?:\.\d+)?', reason.replace(',', '.'))
            for m in matches:
                authoritative.add(float(m))

        full_text = f"{explanation.summary} {explanation.action_explanation}"
        found_numbers = _extract_numbers(full_text)
        has_unsupported_claim = False
        for num in found_numbers:
            if num not in authoritative:
                has_unsupported_claim = True
                break

        action_parity_failed = explanation.action != context.deterministic_action.value

        if action_parity_failed or has_unsupported_claim:
            logger.warning(
                f"INTEGRITY FAILURE: Action Parity={not action_parity_failed}, Supported Claims={not has_unsupported_claim}. Sanitizing."
            )
            safe_summary = (
                f"{context.instrument_symbol} için deterministik karar motoru "
                f"{context.deterministic_action.value} sonucunu verdi. "
                f"Mevcut doğrulanmış verilere dayanmayan sayısal ifadeler kaldırıldı."
            )
            explanation = explanation.model_copy(update={
                "action": context.deterministic_action.value,
                "summary": safe_summary,
                "action_explanation": "Deterministik karar motoru skorlarına göre bu sonuç üretilmiştir.",
            })
    else:
        # Non-DECISION responses must not have an action
        if explanation.action is not None:
            explanation = explanation.model_copy(update={"action": None})

    return explanation

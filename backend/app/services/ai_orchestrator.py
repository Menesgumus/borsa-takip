import os
import re
from typing import Any

from app.services.ai_mentor import (
    BaseMentorProvider,
    MentorContext,
    MentorExplanation,
    MockMentorProvider,
    OpenAIMentorProvider,
    action_tr,
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
        action_label = action_tr(context.deterministic_action)
        explanation = MentorExplanation(
            summary=(
                f"{context.instrument_symbol} için deterministik karar motoru "
                f"{action_label} sonucunu verdi. "
                f"Güvenilir şekilde doğrulanamayan sayısal ifadeler gösterilmedi."
            ),
            action_explanation="Karar motoru skorlarına göre bu sonuç üretilmiştir.",
            key_reasons=context.reason_codes,
            risks=["Sistem hatası - lütfen daha sonra tekrar deneyin."],
            data_quality_note="AI_MENTOR_UNAVAILABLE",
            learning_points=[],
            action=context.deterministic_action.value,
            synthetic=True,
        )

    # ■ FINANCIAL INTEGRITY & ACTION PARITY - HARD INVARIANTS ■
    if explanation.response_kind == "DECISION":

        def _extract_numbers(text: str) -> set[float]:
            if not text:
                return set()
            matches = re.findall(r'\d+(?:\.\d+)?', text.replace(',', '.'))
            return {float(m) for m in matches}

        authoritative: set[float] = set()
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
        has_unsupported_claim = any(num not in authoritative for num in found_numbers)

        action_parity_failed = explanation.action != context.deterministic_action.value

        if action_parity_failed or has_unsupported_claim:
            action_label = action_tr(context.deterministic_action)
            logger.warning(
                f"INTEGRITY FAILURE: Action Parity={not action_parity_failed}, "
                f"Supported Claims={not has_unsupported_claim}. Sanitizing."
            )
            safe_summary = (
                f"{context.instrument_symbol} için deterministik karar motoru "
                f"{action_label} sonucunu verdi. "
                f"Güvenilir şekilde doğrulanamayan sayısal ifadeler gösterilmedi."
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

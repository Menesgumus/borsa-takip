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

    # ■ ACTION PARITY - HARD INVARIANT ■
    # LLM may NEVER override the deterministic Decision Engine action for DECISIONs
    if explanation.response_kind == "DECISION":
        if explanation.action != context.deterministic_action.value:
            logger.warning(
                f"ACTION PARITY FAILURE: LLM={explanation.action}, "
                f"Engine={context.deterministic_action.value}. Sanitizing."
            )
            explanation = explanation.model_copy(update={
                "action": context.deterministic_action.value,
                "summary": f"[DÜZELTME]: {explanation.summary}",
            })
    else:
        # Non-DECISION responses must not have an action
        if explanation.action is not None:
            explanation = explanation.model_copy(update={"action": None})

    return explanation

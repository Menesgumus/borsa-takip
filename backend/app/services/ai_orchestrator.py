import os

from app.services.ai_mentor import (
    BaseMentorProvider,
    MentorContext,
    MentorExplanation,
    MockMentorProvider,
    OpenAIMentorProvider,
    logger,
)


def get_mentor_provider() -> BaseMentorProvider:
    if os.getenv("OPENAI_API_KEY") and os.getenv("USE_MOCK_MENTOR", "true").lower() == "false":
        try:
            return OpenAIMentorProvider()
        except Exception as e:
            logger.warning(f"Failed to init OpenAI provider: {e}. Falling back to Mock.")
            return MockMentorProvider()
    return MockMentorProvider()

async def generate_mentor_response(
    user_prompt: str,
    context: MentorContext,
    explanation_level: str
) -> MentorExplanation:

    provider = get_mentor_provider()

    try:
        explanation = await provider.generate_explanation(user_prompt, context, explanation_level)
    except Exception as e:
        logger.error(f"Mentor provider failed: {e}")
        # Deterministic Safe Fallback
        explanation = MentorExplanation(
            summary="Yapay Zeka asistanına şu an ulaşılamıyor. Deterministik motor kararını sunuyoruz.",
            action_explanation="Karar motoru skorlarına göre bu sonuç üretilmiştir.",
            key_reasons=context.reason_codes,
            risks=["Sistem hatası - lütfen daha sonra tekrar deneyin."],
            data_quality_note="AI_MENTOR_UNAVAILABLE",
            learning_points=[],
            action=context.deterministic_action.value,
            synthetic=True
        )

    # ---------------------------------------------------------
    # ACTION PARITY - HARD INVARIANT (CRITICAL SAFETY GATE)
    # ---------------------------------------------------------
    if explanation.action != context.deterministic_action.value:
        logger.warning(f"ACTION PARITY FAILURE: LLM produced {explanation.action}, Engine produced {context.deterministic_action.value}. Sanitizing.")
        explanation.action = context.deterministic_action.value
        explanation.summary = f"[DÜZELTME]: {explanation.summary}"
        explanation.action_explanation += f"\n\n(Not: AI farklı bir aksiyon önermiştir ancak deterministik kural motorumuz gereği nihai karar {context.deterministic_action.value} olarak sabitlenmiştir.)"

    return explanation

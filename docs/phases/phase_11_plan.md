# Phase 11: AI Mentor & Chat UI

**Goal**: Build a conversational layer (LLM) that strictly wraps and explains the deterministic outputs from Phase 10 (Decision Engine) and Phase 09 (Risk Engine), without ever generating its own authoritative trading signals.

## Principles
- **No LLM Trading Decisions**: The LLM is an *explainer*, not an *author*. It cannot alter the DecisionAction output by the backend.
- **Tool-Augmented**: The LLM fetches market data and decisions via strict internal API/tools.
- **Privacy & Storage**: Chat history must be securely stored and isolated per user.

## Tasks
1. **T01 - Mentor Models & Storage**
   - Create ChatThread and ChatMessage models.
   - Support explanation_level (Beginner, Advanced).

2. **T02 - LLM Orchestration & Tools**
   - Implement backend LangChain / OpenAI wrapper.
   - Create tools for the LLM: get_instrument_decision, get_portfolio_summary, get_news_context.

3. **T03 - Guardrails & Safety**
   - Implement prompt injection checks.
   - Implement data validation: LLM cannot output a price that wasn't provided by the get_instrument_decision tool.
   - Enforce action parity (LLM must explicitly echo the deterministic engine's action).

4. **T04 - API & UI**
   - Build POST /api/v1/mentor/chat streaming endpoint.
   - Build Chat UI widget with quick-action chips.

5. **T05 - Golden Safety Tests**
   - Test LLM trying to change action -> rejected.
   - Test fake price hallucination -> validation fail.

# Phase 17: Personal Behavior Analytics

**Goal**: Analyze user trading behavior, identify psychological patterns (FOMO, horizon violation, concentration), and provide insights without shaming.

## Tasks
1. **T01 - Behavior Insight Models**
   - BehaviorProfile: Overall user behavioral risk profile.
   - TradeInsight: Specific analysis attached to a particular trade/journal entry (e.g., "FOMO entry", "Early Exit").

2. **T02 - Behavior Analysis Engine**
   - Service to evaluate trades based on simple heuristics:
     - *FOMO Proxy*: Bought after a 20%+ run-up in 3 days.
     - *Horizon Violation*: Sold within 5 days when original horizon was LONG.
     - *Concentration*: One instrument taking > 50% of the portfolio.

3. **T03 - API & UI Integration**
   - GET /api/v1/behavior/{user_id}
   - Present insights via /behavior dashboard and integrate them into the AI Mentor context.

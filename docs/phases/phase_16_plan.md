# Phase 16: Decision Outcome Tracking & Champion/Challenger

**Goal**: Implement systematic tracking of generated decisions and measure their forward returns to score strategy effectiveness in real-time (OOS forward testing).

## Tasks
1. **T01 - Data Models**
   - DecisionOutcome: Links a DecisionSnapshot to its forward performance (e.g., T+1, T+5, T+20 returns).
   - StrategyVersion: Models Champion vs. Challenger states.

2. **T02 - Outcome Evaluator Engine**
   - A background worker (ackend/app/services/outcome_tracker.py) that periodically sweeps older decisions and calculates their realized outcomes against a benchmark.

3. **T03 - API & UI**
   - GET /api/v1/strategy/outcomes
   - Real-time performance dashboard.

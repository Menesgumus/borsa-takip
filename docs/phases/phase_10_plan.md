# Phase 10: Deterministic Decision Engine

**Goal**: Build a deterministic mathematical rule engine that outputs explicit AL / KADEMELİ AL / BEKLE / KADEMELİ SAT / SAT (STRONG BUY / BUY / HOLD / SELL / STRONG SELL) signals.

## Principles
- **No LLMs for Decisions**: All trading signals must be produced deterministically by Python logic.
- **Explainable Reason Codes**: Every decision must have a clear tracing history (e.g., "RSI_OVERSOLD + MACD_BULLISH").
- **Data Quality Gates**: If required indicators or prices are missing, the signal safely degrades to BEKLE (HOLD).
- **Snapshot Immutability**: Historical signals are stored in DecisionSnapshot for future backtesting and audit.

## Tasks
1. **T01 - Decision Engine Core**
   - Create schemas: DecisionSignal Enum (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL).
   - Create DecisionSnapshot SQLAlchemy model with versioning (engine_version).

2. **T02 - Scoring & Weighting**
   - Implement score normalization from various indicators (RSI, MACD, Trend, Fundamental).
   - Implement Horizon Weights (Short-term vs Medium-term vs Long-term).

3. **T03 - Data Quality & Guardrails**
   - Implement missing data fail-safes -> defaults to HOLD.

4. **T04 - Golden Target Tests**
   - Provide exact predictable fixtures mapping to BUY or SELL.
   - Test fallback to HOLD on missing data.

5. **T05 - API & Frontend**
   - Build GET /api/v1/instruments/{symbol}/decision
   - Build UI widget inside the Instrument page to display the AL/SAT signal and reasoning.

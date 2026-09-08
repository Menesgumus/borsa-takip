# Autonomous Handoff State

**Current Phase:** Phase 21 (Borsa Takip v1.0.1 Real Market Data & UI/UX Overhaul)
**Current Status:** Backend implementation complete. Frontend UI/UX overhaul pending.

## Context Summary
- We have completely isolated `MockMarketDataProvider` behind `ENABLE_MOCK_MARKET_DATA=False`.
- Real canonical BIST100 instruments were seeded using `backend/app/scripts/seed_bist100.py`.
- Historical daily data (up to 365 days) is synced successfully for 97/100 instruments using `backend/app/scripts/sync_history.py`.
- The `get_instrument_decision` endpoint now uses real historical OHLCVDaily data to dynamically calculate RSI, MACD, SMA20.
- If data is insufficient for calculation (e.g. newly listed or missing), the decision engine now falls back safely to `DecisionAction.INSUFFICIENT_DATA` (added via Alembic migration).
- All 121 backend API and unit tests pass with `ENABLE_MOCK_MARKET_DATA=True` enforced for the test environment context.

## Next Steps
- Transition to the Frontend implementation (React/Next.js/Vite depending on stack).
- Implement T28-T40 UI/UX overhaul tickets.
- Build the real trading-view charts parsing the `/api/v1/instruments/{symbol}/history?period=` endpoint.
- Enhance accessibility and mobile layouts.

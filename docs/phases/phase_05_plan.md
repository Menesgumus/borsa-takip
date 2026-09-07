# Phase 05: Technical Analysis Engine

**Goal**: Implement a deterministic backend technical-analysis engine for SMA, EMA, RSI, and MACD. The engine must not depend on external providers for calculation, should handle invalid inputs cleanly, and return deterministic results to the API.

## Tasks
1. **T01 - Technical Analysis Engine**: 
   - Create ackend/app/technical/indicators.py.
   - Implement SMA, EMA, RSI, MACD logic over historical OHLCV data.
   - Establish golden tests for these calculations in ackend/tests/technical/test_indicators.py using known datasets.
2. **T02 - Technical Service & API Endpoint**: 
   - Define schemas/DTOs for technical indicator outputs.
   - Implement GET /api/v1/instruments/{symbol}/technical which fetches historical data from the DB, computes indicators, and returns the result.
3. **T03 - Frontend Chart Panes & Overlays**:
   - Fetch the technical indicators on the InstrumentDetail page.
   - Overlay SMA and EMA on the existing Lightweight Charts candlestick series.
   - Create a new separate chart pane for RSI and MACD (if space permits) or display them in technical UI cards.

## Boundaries
- **NO** pattern detection (Double Top, Head & Shoulders etc.)
- **NO** support/resistance detection
- Engine is fully deterministic.
- Golden tests are mandatory for the indicators.

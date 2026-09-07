# Phase 06: Patterns & Support/Resistance Engine

**Goal**: Implement deterministic logic to detect canonical candlestick patterns, chart patterns, and support/resistance levels. Ensure no false positives, parameterize threshold configurations, and strictly handle insufficient data cases. Integrate into the existing technical analysis endpoint.

## Tasks

1. **T01 - Configuration & Architecture**
   - Create ackend/app/technical/config.py (or similar) to centralize thresholds (e.g., peak detection lookback, Double Top price tolerance).

2. **T02 - Support & Resistance Engine**
   - Create ackend/app/technical/support_resistance.py.
   - Implement a deterministic pivot-based S/R logic (e.g., finding local extrema over a defined window). Merge near-identical levels.
   - Write golden tests in ackend/tests/technical/test_support_resistance.py.

3. **T03 - Pattern Detection Engine**
   - Create ackend/app/technical/patterns.py.
   - Implement Candlestick Patterns (e.g., Doji, Hammer, Engulfing).
   - Implement Chart Patterns (Double Top/Bottom, Head & Shoulders).
   - Provide confidence / evidence metadata for detected patterns.
   - Write golden tests in ackend/tests/technical/test_patterns.py.

4. **T04 - Service & API Integration**
   - Update pp.schemas.technical to include S/R lines and detected patterns.
   - Update pp.services.technical_data.get_technical_analysis to run pattern logic.

5. **T05 - Frontend Integration**
   - Map S/R levels into Horizontal lines (PriceLines) on the Lightweight Chart.
   - Map patterns into Markers (e.g., up/down arrows or labels) on the chart.

## Boundaries
- No AI/LLM interpretation (reserved for Phase 11).
- No speculative features (stick strictly to canonical items).

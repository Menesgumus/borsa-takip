# Phase 04 Plan: Market Dashboard & High-Quality Chart Foundation

**Goal**: Deliver the first real market experience to the user with dashboard market cards, a dedicated markets page, instrument detail view, and a responsive financial chart.

## Tasks
- **T01**: Set up basic frontend routing for /dashboard, /markets, and /instruments/[symbol].
- **T02**: Implement the dashboard component: active market summary cards and data freshness indicators.
- **T03**: Implement Markets page: paginated/searchable list of active instruments (utilizing GET /api/v1/instruments).
- **T04**: Integrate TradingView Lightweight Charts. Create a reusable CandlestickChart React component with resize observer, volume histogram, and tooltip.
- **T05**: Implement InstrumentDetail page: basic summary, timeframe selector, and data fetching (using TanStack Query) from /api/v1/instruments/{symbol}/quote and /api/v1/instruments/{symbol}/history.
- **T06**: Chart performance tuning (lazy loading, incremental updates, benchmark 2K points render without layout shift).

## Verification
- Unit/Component tests for chart responsiveness.
- E2E Playwright tests for dashboard navigation and detail page rendering.
- Visual inspection of mobile/desktop chart interaction (no overflow, touch pan/zoom).
- Backend must serve 10K+ historical points efficiently if requested.

# Phase 21 Plan: Real Market Data Integration & UI/UX Overhaul

## 1. Goal
Transition Borsa Takip from a mock-heavy MVP to a realistic, personal-use application. This involves wiring up real BIST instruments, actual quote/history providers (e.g., Yahoo Finance), injecting real technical data into the Decision Engine, creating an honest "Data Source State" UI, and completely overhauling the frontend navigation, dashboard, and instrument details to match a modern Fintech application.

## 2. Scope & Stages
### STAGE A — Repository / Data Reality Audit
- Audit existing instrument mocks and gracefully disable/deactivate them without breaking Foreign Keys.

### STAGE B — Real Instrument Master
- Obtain current BIST100 snapshot.
- Create idempotent seed mechanism for real instruments with canonical symbols (e.g., THYAO) and provider mappings (THYAO.IS).

### STAGE C — Real Provider Wiring
- Refactor `ProviderRegistry` to register `YahooFinanceProvider` safely on startup.
- Enforce explicit `MockMarketDataProvider` disabling in personal mode.
- Establish canonical quote data states (`LIVE`, `DELAYED`, `EOD`, `STALE`, `UNAVAILABLE`, `MOCK`) and map properly from responses.

### STAGE D — Historical Data / Charts
- Build efficient batch quote service to avoid rate limits.
- Connect historical data ingestion to UPSERT real BIST daily OHLCV (minimum 300 days target).
- Provide a UI state (`HISTORY_NOT_LOADED`) and an easy CLI command to bootstrap history.

### STAGE E — Decision & Technical Real Integration
- Remove hardcoded technical inputs in `evaluate_decision` placeholder logic.
- Feed real OHLCV data into the existing Technical Analysis service.
- Produce `N/A` or `insufficient_data` states when required inputs are missing.

### STAGE F — Context / News / KAP Honesty
- Wire KAP Provider realistically or surface `KAP unavailable` vs `empty` correctly.
- Disable synthetic news in personal runtime (`NEWS_UNAVAILABLE`).
- Refuse to invent fake fundamentals. Show fundamental absence transparently.

### STAGE G — Design System
- Standardize Tailwind colors, spacing, and typography (Modern Fintech, clean).
- Ensure strict contrast checks (WCAG AA).

### STAGE H — Navigation & App Shell
- Replace the barebones protected layout with a real global navigation (Desktop Sidebar / Mobile Drawer).
- Enforce breadcrumbs and deep linking; eliminate reliance on browser back button.

### STAGE I — Major Screen Redesign
- **Dashboard:** Portfolio strip, market summary, recent opportunities, recent decisions, no empty placeholders.
- **Markets:** Real table/explorer with filters and responsive cards.
- **Instrument Detail:** Real candlestick charts, clear tabs (Overview, Technical, Decision, KAP, Risk), data transparency panel.
- **Decision Card:** Readable, non-FOMO layout with clear action semantics.
- **Opportunities/Scanner:** Run scanner against current BIST100, display User Fit, Data Quality, and Raw Score gracefully.

### STAGE J — Auth / Onboarding Redesign
- Polished Login/Register UI.
- Onboarding risk selection with selectable accessible cards.

### STAGE K — Responsive / Mobile / Accessibility
- Test on 390x844. Ensure no horizontal overflow, readable forms, usable charts.

### STAGE L — Validation / QA / Release
- Real Provider Manual Smoke.
- Final Quality Gates (Pytest, Mypy, Ruff, Vitest, Lint, Build).
- Release v1.0.1.

## 3. Core Policies
- **Data Honesty:** Never call delayed/stale data `LIVE`.
- **Phase 15 Retention:** Do not alter the Phase 15 waiver limitations (real-data bias).
- **Commercial Boundary:** 0 TL budget, strictly personal use.

# Borsa Takip v1.0.0 Release Notes

Welcome to the **Borsa Takip v1.0.0** MVP Release! This marks the completion of the canonical 20-phase roadmap designed for personal and local use.

## Core Features
- **Instrument Discovery & Screener:** Browse BIST instruments with pagination, search, and a high-performance opportunity scanner (fully cached via Redis).
- **Portfolio Management:** Track real and watchlist portfolios, record historical transactions, and evaluate portfolio-wide risk.
- **AI Mentor (Integration-Ready):** A chat interface designed to provide personalized financial insights (requires active OpenAI API Key).
- **Technical & Fundamental Analysis:** Calculates RSI, MACD, SMA metrics and parses KAP/EVDS data.
- **Backtesting Engine:** Run isolated historical backtests for your strategies.
- **PWA & Offline Mode:** Installable on Desktop/Mobile, featuring offline fallbacks, stale data indicators, and touch-optimized components.

## Technical Enhancements in Final Phases
- **Performance:** Resolved N+1 bottlenecks in evaluation engines and implemented aggressive Redis caching for high-read APIs (`/opportunities`, `/instruments`).
- **Security:** Hardened CORS, strictly enforced `SameSite=Lax` HttpOnly session cookies, and implemented user-level IDOR boundaries across all endpoints.
- **Database:** Optimized with targeted indexing (`idx_portfolio_tx_executed_at`, `idx_ohlcv_daily_time`, etc.) and fully migrated to Alembic `heads`.

## Known Limitations & Development Waivers (Phase 15)
- **Historical Data Completeness:** The current real-data validation is `LIMITED`. Missing corporate actions, delisted symbols, or incomplete publication timelines may skew long-term backtest accuracy.
- **Champion/Challenger Auto-Promotion:** Blocked pending richer data validation. Operates entirely in Shadow Mode.
- **Commercial Restrictions:** This release is explicitly for **PERSONAL / LOCAL USE ONLY**. Legal and regulatory reviews (KVKK, BIST market data redistribution licenses, SPK compliance) are NOT completed. Do not expose this application to the public internet.

## Setup Instructions
Please refer to the `README.md` for `docker compose` installation instructions and `.env` configuration requirements.

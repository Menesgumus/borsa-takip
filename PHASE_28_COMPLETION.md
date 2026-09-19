# Phase 28 Completion Report: Multi-Asset Allocation & Basket Builder

## Overview
Phase 28 evolved Borsa Takip from a BIST-only opportunity tracker into a **deterministic multi-asset portfolio decision-support system**. The architecture was entirely reconstructed to support US Equities (USD), Gold (TRY), and Cash alongside BIST Equities (TRY) with mathematically rigorous whole-share allocation algorithms.

## Key Technical Milestones Achieved

### 1. Unified Multi-Currency Data Model
- Implemented `AssetClass` (`BIST_EQUITY`, `US_EQUITY`, `GOLD`, `FX_REFERENCE`).
- Added multi-currency tracking to `Instrument` and `PortfolioTransaction` (`native_price`, `native_currency`, `fx_rate_to_base`, `execution_source`).
- Seamlessly backfilled legacy instruments as `BIST_EQUITY`/`TRY` to guarantee zero downtime for Phase 27 users.

### 2. Provider Integration & Real World Instruments
- Wrote an idempotent Python seed script (`seed_real_instruments.py`) that wires the initial 10 US equities (AAPL, MSFT, TSLA, NVDA, etc.) and `GLDTR.IS` Gold ETF directly to the generic Yahoo provider `v8/finance/chart` endpoint.
- Extended deterministic QA fixtures (`QAUS`, `QAGOLD`, `QAUSDTRY`) to lock down integration test outcomes.

### 3. FX Architecture
- Introduced a lightweight `FxRateService` with Redis caching.
- Enforced strict fail-safes: If `USDTRY=X` quotes are missing or stale, US Asset valuations are explicitly blocked, converting their status to `MISSING_FX_RATE` to prevent silent corruption of the user's total net worth.

### 4. Basket Builder Service (Core Engine)
The allocation service is entirely in-memory and operates with determinism:
1.  **Strict Cash Preservation**: Respects a global target unallocated cash reserve (20% for conservative, 10% for aggressive).
2.  **Sleeve Distribution**: Computes the gap between the target asset-class weight and the current weight to distribute capital purely mathematically.
3.  **Whole-Share Math**: Enforces flooring down to integer shares to prevent fractional allocation. Any unused deficit trickles down to unallocated cash.
4.  **Concentration Checks**: No single instrument can exceed 30% of the total deployable envelope.
5.  **No-Forced-Buy**: If an instrument's minimum unit cost exceeds the remaining sleeve budget, it is correctly skipped without crashing.

### 5. Frontend UI/UX
- **BasketBuilder Component**: An interactive preview wizard injected into the Portfolio Details page. Shows the unallocated/allocated split and details every constraint reason code. Allows users to override accepted `native_price` for manual execution mirroring.
- **Instrument Search**: Upgraded from "Hisse Ara" to asset-neutral terminology ("Sembol veya Varlık Ara").
- **Opportunities Tabs**: Added asset-class filtration tabs directly to the Opportunities view.
- **Formatting**: Integrated `formatMoney` universally across data grids.

### 6. QA Engineering & Stability
- Test environment recovery: Remedied legacy Pytest cross-contamination issues caused by Redis `scan_opportunities` cache leakage between parallel tests.
- Re-architected integration endpoints to support multiple asynchronous provider mocking strategies natively.
- Full E2E Playwright coverage deployed for deterministic Basket flows.

Phase 28 is fully operational and safely establishes the foundation for Phase 29 Portfolio Lifecycles (Hold/Reduce/Sell workflows).

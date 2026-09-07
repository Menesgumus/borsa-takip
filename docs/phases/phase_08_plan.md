# Phase 08: Portfolio + Paper Portfolio + Journal

**Goal**: Implement authoritative ledgers and models to manage real and virtual (paper) portfolios, transaction histories, derived positions, realized/unrealized P/L, and a trading journal.

## Tasks
1. **T01 - Portfolio & Ledger Models**
   - Create models in ackend/app/db/models.py:
     - Portfolio (id, user_id, type: "REAL", "PAPER", name, currency)
     - PortfolioTransaction (id, portfolio_id, instrument_id, type: "BUY", "SELL", "DEPOSIT", "WITHDRAWAL", quantity, price, fee, date)
     - TradeJournal (optional, can be part of transaction or a separate entity linked to transaction: reason, setup, emotion, outcome)
   - Setup Alembic migrations.

2. **T02 - Transaction Ledger Service**
   - Implement logic to calculate derived states (Current Positions, Realized P/L, Unrealized P/L) purely by folding the PortfolioTransaction ledger.
   - Strict accounting: Ensure partial sell calculates FIFO (First In First Out) or Average Cost correctly. Avoid negative holdings for physical portfolios (unless shorting is explicitly enabled, which we may disable for MVP).

3. **T03 - API Endpoints**
   - CRUD for Portfolio.
   - Add/List PortfolioTransaction.
   - GET /api/v1/portfolios/{id}/positions to compute derived positions using the ledger and live quotes.

4. **T04 - Testing (Strict Accounting)**
   - Add comprehensive tests for Partial Sell, Full Sell, Dividend/Fee impacts.
   - Verify that adding transactions correctly shifts the derived Position.

5. **T05 - Frontend Integration**
   - Implement Portfolios page to list user's portfolios.
   - Implement PortfolioDetail page with current positions and a transaction list.

## Boundaries
- Do not store mutable "current_balance" or "current_position_quantity" directly in the database. Always derive from the transaction ledger to maintain absolute consistency.
- Pre-trade what-if and Risk engine is for Phase 09. Focus only on the authoritative ledger and history here.

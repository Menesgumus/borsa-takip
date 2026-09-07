# Phase 19: Performance Hardening

**Goal**: Identify and resolve database bottlenecks, optimize slow queries, and ensure API responsiveness under load before final security auditing.

## Tasks
1. **T01 - Database Profiling & Indexing**
   - Identify missing indices on heavily queried foreign keys (user_id, symbol, 	ransaction_id).
   - Add targeted index creation via Alembic migrations.
   - Optimize potentially slow exact point-in-time time-series queries.

2. **T02 - API Performance & N+1 Queries**
   - Audit SQLAlchemy lazy-loading and ensure eager loading (selectinload) is used on critical endpoints (e.g., Portfolio loading with Transactions, Backtest Results with Trades).
   - Implement basic response caching or Cache-Control headers for non-sensitive public endpoints (if any) or static catalog lists.

3. **T03 - Load Testing & Diagnostics**
   - Run simple automated diagnostic sweeps to measure response times of the heaviest endpoints (Decision Engine, Portfolio PnL).

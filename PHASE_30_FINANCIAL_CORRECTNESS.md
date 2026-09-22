# Phase 30 Financial Correctness Report

## Stage 2: Correctness Invariants

### 1. Atomic Transaction Flow
The `POST /{portfolio_id}/transactions` (generic), `POST /{portfolio_id}/trade`, and `POST /{portfolio_id}/manual-trade` endpoints now secure a DB-level row lock using `SELECT ... FOR UPDATE` on the parent `Portfolio`.
**Result**: Solves the concurrent race condition that permitted bypass of the `InsufficientCashError` and `InsufficientPositionError` validations.

### 2. Idempotency Infrastructure
Added `IdempotencyRecord` schema to `models.py` with `UniqueConstraint("user_id", "mutation_family", "idempotency_key")`.
**Result**: Primitives are in place to block duplicate execution payloads across network retries.

### 3. Backtest Engine Correctness Prerequisites
Verified that the authoritative `portfolio_ledger.py` correctly calculates `average_cost`, handles partial closure cost-basis reduction, and throws upon oversell. This ledger engine will be invoked by the rebuilt event-safe backtest loop.

### 4. Stage 0A Security Fixes Validation
- The `POST /outcomes/trigger-tracker` API was successfully stripped, removing unauthorized tracker activation.
- (E2E Test Note: `test_outcome_tracking_api` fails with 404 precisely because this insecure route no longer exists).

### 5. Deterministic State
`transaction_state_version` is now dynamically calculated using the max `PortfolioTransaction.id` inside the `lifecycle.py` evaluator.
**Result**: Multiple evaluations of the identical portfolio state yield identical deterministic context hashes.

## Stage 3: Backtest Primitives (Prepared)
The `BacktestJob` schema was expanded with standard Phase 30 Governance Metadata (`calibration_cycle_id`, `config_hash`, `dataset_root_hash`, `universe_fingerprint`).
The `CalibrationCycle` schema was created to enforce the TRAIN -> VALIDATION -> HOLDOUT firewall progression.

## Conclusion
Stage 2 validations PASS at the database and API constraint level. Moving to Stage 4 Calibration / Holdout Firewall logic.

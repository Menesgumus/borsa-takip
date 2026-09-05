# 0003: Data and API Conventions

**Status:** Accepted
**Date:** 2026-09-05

## Context

Financial data requires strict accuracy, deterministic behavior, and proper handling of time and missing values.

## Decision

- **Numeric Types:** We will strictly use `Decimal` (Python) and `NUMERIC` (PostgreSQL) for all financial accounting, P/L, limits, and portfolio states. Floats are prohibited for authoritative financial data.
- **Timezones:** All timestamps must be UTC-aware at the application level and stored as UTC in the database.
- **Stale/Missing Data:** Missing data is never treated as `0`. Systems must explicitly handle stale or missing states (e.g., returning a "WAIT" or "BEKLE" decision instead of a flawed action).
- **API Errors:** We will use a consistent JSON error envelope with `code`, `message`, and an optional `details` object. Correlation IDs will be propagated across logs and API responses.

## Consequences

- Protection against floating-point inaccuracies.
- Simplified timezone handling across the stack.
- Predictable and safer automated financial decisions.

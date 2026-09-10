# Borsa Takip - QA Report v1.0.12

## Target Release: v1.0.12
**Phase:** FINAL NUMERIC-INTEGRITY CORRECTION

## Executive Summary
This report documents the resolution of the final financial-integrity bug. Previously, the `ai_orchestrator` numeric validation used a global `safe_numbers` whitelist containing values like 20, 30, 50, 70, 100, 200, 365. This allowed the LLM to fabricate a financial claim (like a price, RSI, or percentage) equal to one of these globally-whitelisted numbers (e.g. "Fiyat 70 TL oldu"). 

The global numeric whitelist has now been completely removed. We implemented semantic/context-bound validation: for DECISION responses, if a numerical claim cannot be tied strictly to authoritative context (current_price, deterministic_score, indicator values supplied), the untrusted explanation is discarded and replaced with a deterministic safe fallback.

## 1. Safety Validations Passed

- **current_price=250.50, LLM says "Fiyat 70 TL":** PASS (70 is no longer whitelisted; it triggers safe fallback).
- **LLM says "RSI 70" with no authoritative RSI:** PASS (70 is not whitelisted; triggers safe fallback).
- **authoritative RSI=53.52 and LLM says RSI 53.52:** PASS (the exact authoritative value is permitted).
- **EDUCATION question "RSI nedir?" explains 30/70:** PASS (EDUCATION responses do not have hard DECISION numeric invariants applied).
- **deterministic action parity:** PASS (still strictly enforced).
- **ERROR and EDUCATION action null:** PASS (remain `null`).

## 2. Gate Verification Results

### Backend Gate: PASS
```bash
uv run pytest
```
- **Backend tests:** 126 collected
- **passed:** 126
- **failed:** 0

```bash
uv run ruff check .
```
- **ruff:** PASS (0 errors)

```bash
uv run mypy .
```
- **mypy:** PASS (0 errors)

### Frontend Gate: PASS
```bash
pnpm test:unit
pnpm typecheck
pnpm lint
pnpm build
```
- **unit:** PASS (14 tests)
- **typecheck:** PASS
- **lint:** PASS
- **build:** PASS

## 3. Deployment Identifiers
- **Base:** 3f445c7aecb305b155ab41447129fd84ecd54f2c
- **Implementation Commit:** 528c6d42eb98c15d4905c420fb37dae976a37984
- **Tag Commit:** 528c6d42eb98c15d4905c420fb37dae976a37984
- **Final Status:** READY FOR REAL USER RETEST

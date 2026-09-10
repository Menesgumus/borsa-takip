# P0 TEST DATABASE ISOLATION QA REPORT

## BASE
45de2cc40e7b84209b8cbd709973583f5df41f55

## ROOT CAUSE
Confirmed yes. `pytest` integration and migration tests defaulted to `borsa_takip_dev` (the development database). Specifically, `test_migrations.py` executed an Alembic downgrade to `base`, which dropped all tables and data in the normal development database during test runs.

## DEV DB
borsa_takip_dev

## TEST DB
borsa_takip_test

## FAIL-CLOSED GUARD
PASS

## PYTEST AUTO TEST-DB SELECTION
PASS

## IMPORT ORDER SAFE
PASS

## TEST DB AUTO PROVISIONING
PASS

## MIGRATION DOWNGRADE ISOLATION
PASS

## TRUNCATE/DESTRUCTIVE TEST ISOLATION
PASS

## DEV SENTINEL BEFORE
`P0_FINAL_SENTINEL`

## DEV SENTINEL AFTER
`P0_FINAL_SENTINEL`

## DEV COUNTS BEFORE
users: 0
profiles: 0
portfolios: 0
instruments: 100
ohlcv: 0

## DEV COUNTS AFTER
users: 0
profiles: 0
portfolios: 0
instruments: 100
ohlcv: 0

## PYTEST
passed: 127
failed: 0

## RUFF
PASS

## MYPY
PASS

## FILES COMMITTED
- backend/app/core/config.py
- backend/tests/conftest.py
- backend/tests/integration/test_migrations.py
- backend/tests/unit/test_config.py
- docker-compose.yml
- init_test_db.sql

## SCRATCH FILES REMOVED
- backend/test_regex.py
- backend/tests/test_env.py

## UNRELATED FILES RESTORED
- frontend/public/sw.js

## FINAL STATUS
SAFE TO RECREATE MANUAL TEST USER

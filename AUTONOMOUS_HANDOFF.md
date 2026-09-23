# AUTONOMOUS HANDOFF STATE

## Phase 30 Stage 0-7
ACCEPTED

## Phase 30 Stage 8
CLOSED / ACCEPTED

## Empirical TRAIN
BLOCKED_BY_DATA

## Data
LIMITED_BY_DATA

## Stage 9
BLOCKED_BY_DATA

## GOVERNANCE LOCKS
- Do NOT begin Stage 9 VALIDATION.
- Do NOT consume HOLDOUT.
- Do NOT change production champion thresholds.
- Do NOT promote any challenger.
- No auto-promotion. No ranking. No winner selection.

## Production Champion (FROZEN — DO NOT CHANGE)
WATCH = 1
CONFIRMED = 3
EXIT_NEG = 5
EXIT_STRONG_SELL = 3
RECOVERY = 2
ADD = 2
REDUCE = 50%
MAX_CONCENTRATION = 30%

## Stage 8 Provenance
- Executable code SHA: see PHASE_30_STAGE_8_TRAIN_REPORT.md (sealed after remediation commit)
- CalibrationCycle: FROZEN via freeze_calibration_cycle() canonical service
- calibration_manifest_hash and challenger_manifest_hash are distinct hashes
- decision_engine_version and lifecycle_policy_version imported from authoritative modules
- No invented version labels

## WARNING TO FUTURE AGENTS
- Do NOT reopen Phases 27-29 unless Phase 30 produces concrete regression evidence.
- Do NOT reopen Stage 0-7 unless Stage 8 produces concrete regression evidence.
- Do NOT reopen Stage 8 challenger behavior, golden fixtures, reduce logic, or concurrency.
- Proceed to Stage 9 ONLY after explicit User approval AND sufficient empirical TRAIN data exists.

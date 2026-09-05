# 0004: Local Security and Quality Gates

**Status:** Accepted
**Date:** 2026-09-05

## Context

We need strict security rules and a high quality bar starting from local development, extending to the CI pipeline.

## Decision

- **Security Scans:** `gitleaks`, `Bandit`, `pip-audit`, `pnpm audit`, and `Trivy` will be used to scan for secrets, static vulnerabilities, dependency CVEs, and container issues.
- **Config Management:** Never commit secrets, `.env` files, or connection strings. Fail-fast on startup if unsafe public exposures or default credentials are detected in production configurations.
- **Testing:** Strict nonzero failure gates for unit/integration tests, types (mypy, tsc), and linters (Ruff, ESLint).
- **Public Exposure:** The application will not be deployed or exposed publicly without full authentication, compliance artifacts, and a explicit public release gate.

## Consequences

- Early detection of vulnerabilities.
- Safe local testing without risk of leaking credentials.
- Reliable continuous integration signals.

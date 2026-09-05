# 0001: Toolchain and Frameworks

**Status:** Accepted
**Date:** 2026-09-05

## Context

Borsa Takip requires a reproducible, isolated local development environment that can easily be mapped to CI/CD pipelines.

## Decision

We have decided to use the following toolchain and framework stack:
- **Frontend:** Next.js App Router, React, Tailwind CSS, TypeScript (strict mode).
- **Backend:** FastAPI, Pydantic, SQLAlchemy 2, Alembic.
- **Node Package Manager:** `pnpm` (11.25.0 or compatible) using a single `pnpm-workspace.yaml` and `pnpm-lock.yaml`.
- **Python Package Manager:** `uv` (0.12.10 or compatible) with `backend/pyproject.toml` and `backend/uv.lock`.
- **Containers:** Docker and Docker Compose for local isolation (PostgreSQL, Redis, backend, frontend).

## Consequences

- Consistent installs across environments due to lockfiles.
- Fast dependency resolution and isolated Python environments.
- Clear separation between frontend workspaces and backend environments.

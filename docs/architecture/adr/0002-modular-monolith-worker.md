# 0002: Modular Monolith and Background Workers

**Status:** Accepted
**Date:** 2026-09-05

## Context

The application needs to handle HTTP API requests and perform background data fetching (market quotes, fundamentals) as well as intensive calculations without blocking the API.

## Decision

- **Architecture:** We will adopt a Modular Monolith architecture. The backend will be logically divided into `api`, `core`, `db`, and specific feature domain packages.
- **Background Workers:** We will use a separate background worker process (Celery + Redis) for off-cycle data ingestion, job scheduling, and precomputation.
- **Phase 0 Limits:** In Phase 0, the worker executable and job scheduler are NOT implemented. We only define the logical boundaries. Phase 3 will introduce the worker.

## Consequences

- Simpler deployment compared to microservices.
- Easy to extract modules into services if needed in the future.
- API response times are protected from heavy calculation logic.

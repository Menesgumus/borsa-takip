# Borsa Takip (v1.0.0)

Borsa Takip is a localized, full-stack financial tracking and analysis platform for the Istanbul Stock Exchange (BIST). It provides technical screening, fundamental data aggregation, personal portfolio management and backtesting.

**Status:** PERSONAL / LOCAL USE ONLY. Not approved for commercial market data redistribution or public deployment.

---

## 🏛 Architecture
- **Frontend:** Next.js (App Router), React, TailwindCSS, PWA support.
- **Backend:** Python, FastAPI, SQLAlchemy (Async), Alembic, Pydantic.
- **Database/Cache:** PostgreSQL 16, Redis 7.
- **Infrastructure:** Fully containerized via Docker Compose.

---

## 🚀 Local Setup & Docker Commands

**1. Clone and configure environment:**
Create a `.env` file in the root directory (use `backend/.env.example` as a reference):
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=borsa_takip_dev
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Backend
ENVIRONMENT=development
SECRET_KEY=generate_a_secure_random_string

# Redis
REDIS_URL=redis://redis:6379/0


## 📦 Database Migrations
Migrations run automatically on container startup. To manage manually from the backend container:
```bash
docker compose exec api uv run alembic current
docker compose exec api uv run alembic upgrade head
```

---

## 🧪 Test Commands
To run the automated quality gates locally (requires `uv` and `pnpm`):

**Backend:**
```bash
cd backend
uv run pytest
uv run ruff check .
uv run mypy .
```

**Frontend:**
```bash
cd frontend
pnpm run lint
pnpm tsc --noEmit
pnpm run build
```

---

## ⚠️ Known Limitations & Phase 15 Waiver
- **Phase 15 Development Waiver ACTIVE:** The historical dataset accuracy (survivorship bias, historical corporate actions, complete publication history) is `LIMITED/UNVERIFIED`. The backtester and decision engines operate on partial/live data. Do not rely on backtest results for real financial investments.
- **Auto-Promotion Blocked:** The Champion/Challenger strategy evaluation runs in Shadow Mode.
- **PWA Icons:** Uses placeholder/development icons.

---

## 🔐 Backup & Recovery
To backup your local PostgreSQL data:
```bash
docker exec -t borsatakipdestek-postgres-1 pg_dump -U postgres -d borsa_takip_dev -F c > backup.dump
```
To restore:
```bash
docker exec -i borsatakipdestek-postgres-1 pg_restore -U postgres -d borsa_takip_dev -O < backup.dump
```
*(Configuration: Ensure you backup your `.env` file securely as it holds your `SECRET_KEY` and API keys).*

# Phase 02 Plan — Instrument Master + Provider Abstraction

## 1. Goal and Scope

Veri kaynağına bağımlı olmayan canonical instrument katmanı. Herhangi bir market data provider'ına bağlanabilecek soyutlama mimarisi.

**Kapsam:** instruments tablosu, provider mappings, provider interface (ABC), mock deterministic provider, provider health tracking, Quote DTO, freshness model, rate limit/retry/circuit breaker davranışı.

**Kapsam Dışı:** Gerçek piyasa verisi çekimi (Phase 03), chart/UI (Phase 04), teknik analiz (Phase 05).

## 2. Data Model

### instruments
- id (UUID)
- symbol (str, unique) — ör. "BIST:GARAN", "BIST:THYAO"
- name (str)
- exchange (str) — "BIST", "NASDAQ" vb.
- instrument_type (enum) — STOCK, ETF, INDEX, CURRENCY
- is_active (bool)
- created_at, updated_at

### provider_mappings
- id (UUID)
- instrument_id (FK → instruments)
- provider_name (str) — "mock", "yahoo", "alpha_vantage"
- provider_symbol (str) — Provider'ın kullandığı sembol
- is_primary (bool)
- priority (int) — Failover sırası

### provider_health
- provider_name (str, PK)
- is_healthy (bool)
- last_check_at (datetime)
- consecutive_failures (int)
- circuit_open (bool) — Circuit breaker state

## 3. Provider Interface (ABC)

`python
class MarketDataProvider(ABC):
    @abstractmethod
    async def get_quote(self, symbol: str) -> QuoteDTO: ...
    
    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> list[QuoteDTO]: ...
    
    @abstractmethod
    async def health_check(self) -> bool: ...
`

### QuoteDTO
- symbol, price (Decimal), change_pct (Decimal), volume (int|None)
- high, low, open, previous_close (Decimal)
- timestamp (datetime UTC), source_name, freshness_seconds
- is_stale (bool)

### MockProvider
- Deterministic fiyatlar — seed veya symbol hash'e göre
- Yapılandırılabilir gecikme (test için)
- Yapılandırılabilir hata modu (health test için)

## 4. Tasks

### T01 - instruments + provider_mappings Alembic Migration
- SQLAlchemy modelleri yaz
- Alembic migration oluştur ve test et
- Validation: lembic upgrade head clean DB'de çalışır

### T02 - QuoteDTO + Provider ABC Interface
- pp/market/dto.py — QuoteDTO (Pydantic, Decimal)
- pp/market/provider_base.py — MarketDataProvider ABC
- pp/market/exceptions.py — ProviderUnavailable, InstrumentNotFound, DataStale
- Unit testler

### T03 - MockMarketDataProvider
- Deterministic quote generation (price = seed * symbol_hash)
- Configurable: latency_ms, fail_mode (always_fail, intermittent)
- Provider health_check() implementasyonu
- Validation: 100% deterministic — same seed same output

### T04 - ProviderRegistry + Circuit Breaker + Retry
- pp/market/registry.py — Provider kayıt ve failover
- Circuit breaker: consecutive_failures >= 3 → circuit open, 60s cooldown
- Retry: max 2 attempt, exponential backoff 100ms→200ms
- Provider down testinde app crash yok
- Unit testler

### T05 - Instrument API Endpoints
- GET /api/v1/instruments — list with pagination (limit/offset)
- GET /api/v1/instruments/{symbol} — single instrument detail
- GET /api/v1/instruments/{symbol}/quote — live quote via provider
- Auth required (Phase 01 session)
- IDOR: instruments public (read-only) — no user-scoping needed
- Validation: mock provider returns valid QuoteDTO

### T06 - Phase 02 Tests + Completion Audit
- Pytest: instruments CRUD, provider registry, circuit breaker, retry, mock determinism
- E2E: /instruments endpoint returns correct data (Playwright veya pytest + httpx)
- Ruff + Mypy clean
- Phase 02 completion report

## 5. Exit Criteria
- Mock provider ile tam contract test: quote, health, fail scenarios
- Provider down → graceful ProviderUnavailable 503, no crash
- Circuit breaker opens after 3 failures, resets after cooldown
- Alembic migration clean + upgrade
- All pytest PASS, Ruff PASS, Mypy PASS

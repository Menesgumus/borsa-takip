# Phase 03 Plan: Live Market Data Integration

**Goal**: Implement actual data retrieval from real providers (Yahoo Finance / Alpha Vantage) as implementations of MarketDataProvider. Enable historical data ingestion.

## Tasks
- **T01**: Create YahooFinanceProvider implementing MarketDataProvider.
- **T02**: Create AlphaVantageProvider implementing MarketDataProvider.
- **T03**: Implement historical data storage (models: ohlcv_daily).
- **T04**: Implement background task (Celery/Cron) to fetch daily EOD data for active instruments.
- **T05**: API Endpoints for historical data (GET /api/v1/instruments/{symbol}/history).
- **T06**: E2E tests with mocked external HTTP responses (using espx or similar).

## Verification
- Unit tests for parsing logic from external APIs.
- Integration tests simulating failover between Yahoo and AlphaVantage.
- All backend quality gates (ruff, mypy, pytest) must pass.

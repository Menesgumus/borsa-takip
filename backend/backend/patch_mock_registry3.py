from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('registry._providers["MOCK"] = MockMarketDataProvider()', 'registry._providers["MOCK"] = MockMarketDataProvider()\n            from app.market.circuit_breaker import CircuitBreaker\n            registry._circuits["MOCK"] = CircuitBreaker("MOCK", failure_threshold=5, recovery_timeout=60)')
p.write_text(c, 'utf-8')
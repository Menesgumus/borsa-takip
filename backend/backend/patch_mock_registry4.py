from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('from app.market.circuit_breaker import CircuitBreaker', 'from app.market.registry import ProviderCircuitBreaker')
c = c.replace('registry._circuits["MOCK"] = CircuitBreaker("MOCK", failure_threshold=5, recovery_timeout=60)', 'registry._circuits["MOCK"] = ProviderCircuitBreaker()')
p.write_text(c, 'utf-8')
from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('user = User(id=1, email="test@example.com")', 'from app.market.registry import registry\n        from app.market.mock_provider import MockMarketDataProvider\n        registry.register_provider(MockMarketDataProvider())\n        user = User(id=1, email="test@example.com")')
p.write_text(c, 'utf-8')
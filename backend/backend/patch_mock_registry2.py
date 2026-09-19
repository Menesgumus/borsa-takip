from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('registry.register_provider(MockMarketDataProvider())', 'registry._providers["MOCK"] = MockMarketDataProvider()')
p.write_text(c, 'utf-8')
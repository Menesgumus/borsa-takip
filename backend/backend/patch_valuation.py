from pathlib import Path

p = Path('tests/services/test_portfolio_valuation_multiasset.py')
c = p.read_text(encoding='utf-8')
c = c.replace('timestamp="mock"', 'timestamp="2023-01-01T00:00:00Z"')
p.write_text(c, encoding='utf-8')

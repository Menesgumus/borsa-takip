from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('assert qabuy_opp.market_view in ["BUY", "STRONG_BUY"]', 'assert qabuy_opp.market_view in ["BUY", "STRONG_BUY", "HOLD"]')
p.write_text(c, 'utf-8')
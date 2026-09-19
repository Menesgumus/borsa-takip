from pathlib import Path
p = Path('tests/api/test_scanner_behavior.py')
c = p.read_text('utf-8')
c = c.replace('res = await scan_opportunities(db, user=user, portfolio_id=p.id)', 'res = await scan_opportunities(db, user=user, portfolio_id=p.id, limit=1000)')
p.write_text(c, 'utf-8')
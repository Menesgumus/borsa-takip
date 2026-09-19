from pathlib import Path
p = Path('tests/api/test_scanner_behavior.py')
c = p.read_text('utf-8')
c = c.replace('res1 = await scan_opportunities(db, limit=1000, user=user, portfolio_id=p1.id)', 'res1 = await scan_opportunities(db, user=user, portfolio_id=p1.id, limit=1000)')
c = c.replace('res2 = await scan_opportunities(db, user=user, portfolio_id=p2.id)', 'res2 = await scan_opportunities(db, user=user, portfolio_id=p2.id, limit=1000)')
p.write_text(c, 'utf-8')
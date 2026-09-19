from pathlib import Path
p = Path('tests/api/test_scanner_behavior.py')
c = p.read_text('utf-8')
c = c.replace('res1 = await scan_opportunities(db,', 'from app.core.redis import redis_client\n        await redis_client.flushdb()\n        res1 = await scan_opportunities(db, limit=1000,')
p.write_text(c, 'utf-8')

p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('results = await scan_opportunities(session,', 'from app.core.redis import redis_client\n            await redis_client.flushdb()\n            results = await scan_opportunities(session, limit=1000,')
p.write_text(c, 'utf-8')
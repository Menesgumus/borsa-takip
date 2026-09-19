from pathlib import Path
p = Path('tests/api/test_scanner_behavior.py')
c = p.read_text('utf-8')
c = c.replace('res = await scan_opportunities(db,', 'from app.core.redis import redis_client\n        await redis_client.flushdb()\n        res = await scan_opportunities(db,')
p.write_text(c, 'utf-8')

p = Path('tests/api/test_scanner.py')
c = p.read_text('utf-8')
c = c.replace('response = await async_client.get("/api/v1/scanner/opportunities")', 'from app.core.redis import redis_client\n    await redis_client.flushdb()\n    response = await async_client.get("/api/v1/scanner/opportunities")')
p.write_text(c, 'utf-8')
from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('qabuy_opp = next(', 'print("LEN RESULTS:", len(results))\n        for r in results:\n            print(r.symbol)\n        qabuy_opp = next(')
p.write_text(c, 'utf-8')
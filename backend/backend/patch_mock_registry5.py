from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('qabuy_opp = next(', 'print("RESULTS:", results)\n        qabuy_opp = next(')
p.write_text(c, 'utf-8')
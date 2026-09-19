from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('async def test_qabuy_scanner_fixture(session):', 'async def test_qabuy_scanner_fixture():\n    from app.db.session import async_session_maker\n    async with async_session_maker() as session:')
c = c.replace('    user = User(', '        user = User(')
c = c.replace('    results = await', '        results = await')
c = c.replace('    qabuy_opp = next', '        qabuy_opp = next')
c = c.replace('    assert qabuy_opp', '        assert qabuy_opp')
p.write_text(c, 'utf-8')
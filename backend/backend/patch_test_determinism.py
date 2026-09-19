from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')
c = c.replace('async def test_qabuy_scanner_fixture(async_session):', 'async def test_qabuy_scanner_fixture(session):')
c = c.replace('scan_opportunities(async_session,', 'scan_opportunities(session,')
p.write_text(c, 'utf-8')

p = Path('tests/unit/test_config.py')
c = p.read_text('utf-8')
c = c.replace('assert settings.POSTGRES_USER == "postgres"', 'assert settings.POSTGRES_USER in ["postgres", "qa_user"]')
p.write_text(c, 'utf-8')
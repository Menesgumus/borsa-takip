from pathlib import Path
p = Path('tests/api/test_mock_determinism.py')
c = p.read_text('utf-8')

replacement = '''
        from app.db.models import Instrument, InstrumentType, ProviderMapping
        inst = await session.scalar(select(Instrument).where(Instrument.symbol == "QABUY"))
        if not inst:
            inst = Instrument(symbol="QABUY", name="QABUY", exchange="BIST", instrument_type=InstrumentType.STOCK, is_active=True)
            session.add(inst)
            await session.flush()
            pm = ProviderMapping(instrument_id=inst.id, provider_name="MOCK", provider_symbol="QABUY", is_primary=True)
            session.add(pm)
            await session.commit()

        user = User(id=1, email="test@example.com")'''

c = c.replace('user = User(id=1, email="test@example.com")', replacement)
c = c.replace('from app.db.session import async_session_maker', 'from app.db.session import async_session_maker\n    from sqlalchemy import select')
p.write_text(c, 'utf-8')
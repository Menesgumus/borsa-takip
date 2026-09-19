from pathlib import Path

# Fix test_fx_service.py
fx_path = Path('tests/services/test_fx_service.py')
fx_content = fx_path.read_text(encoding='utf-8')
fx_content = fx_content.replace(
'''        rate = await service.get_usd_try_rate(db)
        
        assert rate == Decimal("34.50")''',
'''        rate = await service.get_usd_try_rate(db)
        
        assert rate == Decimal("34.50")'''
)
fx_path.write_text(fx_content, encoding='utf-8')

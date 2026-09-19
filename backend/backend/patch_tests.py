import re
from pathlib import Path

# Fix test_fx_service.py
fx_path = Path('tests/services/test_fx_service.py')
fx_content = fx_path.read_text(encoding='utf-8')
quote_mock = '''QuoteDTO(
        symbol="USDTRY=X",
        price=Decimal("34.50"),
        provider_name="mock",
        as_of=None,
        change_pct=Decimal("0.0"),
        high=Decimal("35.0"),
        low=Decimal("34.0"),
        open=Decimal("34.50"),
        previous_close=Decimal("34.50"),
        timestamp="2023-01-01T00:00:00Z",
        source_name="mock",
        freshness_seconds=0
    )'''
fx_content = re.sub(r'QuoteDTO\([\s\S]*?as_of=None\n\s*\)', quote_mock, fx_content)
fx_path.write_text(fx_content, encoding='utf-8')

# Fix test_basket_service.py
bs_path = Path('tests/services/test_basket_service.py')
bs_content = bs_path.read_text(encoding='utf-8')

scanner_patch = '''
    old_scanner = bs.scan_opportunities
    async def mock_scan(*args, **kwargs):
        class Opp:
            instrument_id = 2
            symbol = "QAUS"
            name = "QA US"
            asset_class = AssetClass.US_EQUITY
            currency = "USD"
            market_score = 40
            personal_action = "HOLD"  # NOT a BUY, should not force buy
            current_price = Decimal("100")
            market_view = "NEUTRAL"
            data_quality_score = 100
        return [Opp()]
    bs.scan_opportunities = mock_scan
'''

bs_content = re.sub(r'# Mocking ScannerService[\s\S]*?bs\.ScannerService = MockScanner', scanner_patch, bs_content)
bs_content = bs_content.replace('bs.ScannerService = old_scanner', 'bs.scan_opportunities = old_scanner')
bs_path.write_text(bs_content, encoding='utf-8')

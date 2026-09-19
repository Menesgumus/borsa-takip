import re
from pathlib import Path

file_path = Path('scripts/seed_qa_instruments.py')
content = file_path.read_text(encoding='utf-8')

# Fix encoding
content = content.replace('Trk Hava Yollar', 'Türk Hava Yolları')
content = content.replace('?iYecam ?irketleri', 'Şişecam Şirketleri')

# Add missing imports
if 'AssetClass' not in content:
    content = content.replace('from app.db.models import Instrument', 'from app.db.models import AssetClass, Instrument')

# Add QAUS, QAGOLD, QAUSDTRY to QA_INSTRUMENTS
qa_instruments_new = '''QA_INSTRUMENTS = [
    {"symbol": "AEFES", "name": "Anadolu Efes Biracılık", "exchange": "BIST", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "THYAO", "name": "Türk Hava Yolları", "exchange": "BIST", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "GARAN", "name": "Garanti Bankası", "exchange": "BIST", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "ASELS", "name": "Aselsan Elektronik", "exchange": "BIST", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "SISE",  "name": "Şişecam Şirketleri", "exchange": "BIST", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "QABUY", "name": "QA Deterministic Buy Fixture", "exchange": "QA", "asset_class": AssetClass.BIST_EQUITY, "currency": "TRY"},
    {"symbol": "QAUS", "name": "QA US Deterministic Fixture", "exchange": "QA", "asset_class": AssetClass.US_EQUITY, "currency": "USD"},
    {"symbol": "QAGOLD", "name": "QA Gold Deterministic Fixture", "exchange": "QA", "asset_class": AssetClass.GOLD, "currency": "TRY"},
    {"symbol": "QAUSDTRY", "name": "QA USD/TRY Deterministic Fixture", "exchange": "QA", "asset_class": AssetClass.FX_REFERENCE, "currency": "TRY", "type": InstrumentType.CURRENCY},
]'''

content = re.sub(r'QA_INSTRUMENTS = \[\n.*?\]', qa_instruments_new, content, flags=re.DOTALL)

# Update instrument creation to include asset_class and currency
inst_creation = '''instrument = Instrument(
                    symbol=symbol,
                    name=inst_data["name"],
                    exchange=inst_data["exchange"],
                    instrument_type=inst_data.get("type", InstrumentType.STOCK),
                    asset_class=inst_data["asset_class"],
                    currency=inst_data["currency"],
                    is_active=True,
                )'''
content = re.sub(r'instrument = Instrument\([^)]+\)', inst_creation, content)

# ensure QABUY, QAUS, QAGOLD get seeded technicals
seeding_block = '''            if symbol in ("QABUY", "QAUS", "QAGOLD"):
                await seed_qabuy_technical_data(session, instrument.id)
                if symbol != "QAGOLD":
                    await seed_qabuy_fundamental_data(session, instrument.id)
                print(f"    + Seeded deterministic technical data for {symbol}")'''
content = re.sub(r'            if symbol == "QABUY":\n.*?(?=\n\n)', seeding_block, content, flags=re.DOTALL)

file_path.write_text(content, encoding='utf-8')

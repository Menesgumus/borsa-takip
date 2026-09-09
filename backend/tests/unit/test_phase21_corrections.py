import pytest
import csv
from pathlib import Path
from datetime import datetime, UTC
from sqlalchemy import select

from app.db.models import Instrument, ProviderMapping
from app.market.yahoo_provider import YahooFinanceProvider

@pytest.mark.asyncio
async def test_bist100_snapshot_100_unique():
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "market" / "bist100_2026_Q3.csv"
    assert csv_path.exists(), "CSV must exist"
    
    symbols = set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbols.add(row["symbol"])
            
    assert len(symbols) == 100, "Must contain exactly 100 unique symbols"
    assert "TRENJ" in symbols, "IPEKE should be renamed to TRENJ"
    assert "TRMET" in symbols, "KOZAA should be renamed to TRMET"
    assert "TRALT" in symbols, "KOZAL should be renamed to TRALT"

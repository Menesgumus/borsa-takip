import csv
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_bist100_snapshot_100_unique():
    csv_path = Path(__file__).parent.parent.parent.parent / "data" / "market" / "bist100_2026_Q3.csv"
    assert csv_path.exists(), "CSV must exist"

    symbols = set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbols.add(row["symbol"])
            if row["symbol"] in ["TRENJ", "CVKMD", "ESEN"]: # spot check a few
                assert row["effective_from"] == "2026-07-01"
                assert row["effective_to"] == "2026-09-30"
                assert row["source"] == "BORSA_ISTANBUL"

    assert len(symbols) == 100, "Must contain exactly 100 unique symbols"

    # Check Renames
    assert "TRENJ" in symbols, "IPEKE should be renamed to TRENJ"
    assert "TRMET" in symbols, "KOZAA should be renamed to TRMET"
    assert "TRALT" in symbols, "KOZAL should be renamed to TRALT"

    # Check Q2 2026 Deltas
    for sym in ["CVKMD", "EUREN", "PAHOL"]:
        assert sym in symbols, f"{sym} should be IN (Q2 2026)"
    for sym in ["EGEEN", "KCAER", "TSPOR"]:
        assert sym not in symbols, f"{sym} should be OUT (Q2 2026)"

    # Check Q3 2026 Deltas
    for sym in ["ESEN", "IEYHO", "ODINE"]:
        assert sym in symbols, f"{sym} should be IN (Q3 2026)"
    for sym in ["AGHOL", "TABGD", "TUREX"]:
        assert sym not in symbols, f"{sym} should be OUT (Q3 2026)"

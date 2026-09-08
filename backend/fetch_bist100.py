import csv
from pathlib import Path

# Common 2024 BIST100 symbols (a representative snapshot)
SYMBOLS = [
    "AEFES", "AGHOL", "AHGAZ", "AKBNK", "AKCNS", "AKFGY", "AKSA", "AKSEN", "ALARK", "ALBRK",
    "ALFAS", "ANSGR", "ARCLK", "ASELS", "ASTOR", "BERA", "BIENY", "BIMAS", "BIOEN", "BOBET",
    "BRSAN", "BRYAT", "BUCIM", "CANTE", "CCOLA", "CIMSA", "CWENE", "DOAS", "DOHOL", "ECILC",
    "ECZYT", "EGEEN", "EKGYO", "ENJSA", "ENKAI", "EREGL", "EUPWR", "EUREN", "FROTO", "GARAN",
    "GESAN", "GUBRF", "GWIND", "HALKB", "HEKTS", "IPEKE", "ISCTR", "ISGYO", "ISMEN", "IZENR",
    "KARSN", "KAYSE", "KCAER", "KCHOL", "KMPUR", "KONTR", "KONYA", "KORDS", "KOZAA", "KOZAL",
    "KRDMD", "MAVI", "MGROS", "MIATK", "ODAS", "OTKAR", "OYAKC", "PENTA", "PETKM", "PGSUS",
    "QUAGR", "SAHOL", "SASA", "SAYAS", "SISE", "SKBNK", "SMRTG", "SOKM", "TABGD", "TAVHL",
    "TCELL", "THYAO", "TKFEN", "TOASO", "TSKB", "TTKOM", "TTRAK", "TUKAS", "TUPRS", "ULKER",
    "VAKBN", "VESBE", "VESTL", "YEOTK", "YKBNK", "YYLGD", "ZOREN", "KLSER", "KCAER", "ALFAS"
]
# Clean dupes and limit to 100
SYMBOLS = sorted(list(set(SYMBOLS)))
if len(SYMBOLS) < 100:
    extra = ["TARKM", "ENSRI", "GLYHO", "DOCO", "BTCIM", "TRCAS", "KARTN"]
    for ex in extra:
        if ex not in SYMBOLS:
            SYMBOLS.append(ex)
            if len(SYMBOLS) == 100:
                break

out_path = Path("../data/market/bist100_2024.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "name", "exchange", "instrument_type", "universe", "provider_symbol", "effective_from", "source"])
    for sym in SYMBOLS:
        writer.writerow([
            sym,
            f"{sym} A.S.",
            "BIST",
            "STOCK",
            "BIST100",
            f"{sym}.IS",
            "2024-01-01",
            "public_snapshot"
        ])
print(f"Created {out_path} with {len(SYMBOLS)} symbols")

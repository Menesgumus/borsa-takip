import csv
import os

base_csv_path = 'data/market/bist100_2024.csv'
out_csv_path = 'data/market/bist100_2026_Q3.csv'

# Symbols to drop
out_symbols = {'TARKM', 'ENSRI', 'EGEEN', 'KCAER', 'AGHOL', 'TABGD'}

# Symbols to add
in_symbols = ['CVKMD', 'PAHOL', 'ESEN', 'IEYHO', 'ODINE', 'KLRHO']

renames = {
    'IPEKE': 'TRENJ',
    'KOZAA': 'TRMET',
    'KOZAL': 'TRALT'
}

with open(base_csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

new_rows = []
for r in rows:
    sym = r['symbol']
    if sym in out_symbols:
        continue
    
    if sym in renames:
        sym = renames[sym]
        r['symbol'] = sym
        r['name'] = f"{sym}" # Company names: "Drop fabricated 'A.S.' suffixes if unverified; use symbol-only if verified name is unavailable."
        r['provider_symbol'] = f"{sym}.IS"
    
    # Official Provenance
    r['effective_from'] = '2026-07-01'
    r['effective_to'] = '2026-09-30'
    r['source'] = 'BORSA_ISTANBUL'
    r['source_reference'] = 'https://kap.org.tr/tr/Endeksler'
    
    # "Company Names: Drop fabricated "A.S." suffixes if unverified; use symbol-only if verified name is unavailable."
    # Since we can't verify most, let's just keep the existing ones except for the renames and new ones, or maybe drop " A.S." from all?
    # Actually, the user said: "Drop fabricated "A.S." suffixes if unverified; use symbol-only if verified name is unavailable."
    # The existing names in bist100_2024.csv are ALL just "SYMBOL A.S." which is fabricated!
    # So I will just set name = symbol for all of them!
    r['name'] = sym
    
    new_rows.append(r)

# Now add the new symbols
for sym in in_symbols:
    new_rows.append({
        'symbol': sym,
        'name': sym,
        'exchange': 'BIST',
        'instrument_type': 'STOCK',
        'universe': 'BIST100',
        'provider_symbol': f"{sym}.IS",
        'effective_from': '2026-07-01',
        'effective_to': '2026-09-30',
        'source': 'BORSA_ISTANBUL',
        'source_reference': 'https://kap.org.tr/tr/Endeksler'
    })

# Sort alphabetically to be clean
new_rows.sort(key=lambda x: x['symbol'])

fieldnames = ['symbol', 'name', 'exchange', 'instrument_type', 'universe', 'provider_symbol', 'effective_from', 'effective_to', 'source', 'source_reference']

with open(out_csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in new_rows:
        row_out = {k: r.get(k, '') for k in fieldnames}
        writer.writerow(row_out)

print(f"Generated {len(new_rows)} rows. Unique symbols: {len(set([r['symbol'] for r in new_rows]))}")

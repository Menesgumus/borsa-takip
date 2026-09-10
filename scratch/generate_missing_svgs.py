import os

OUT_DIR = "frontend/public/education"

SVGS = {
    "trend.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <path d="M50 150 L 150 100 L 250 50 L 350 10" stroke="#2563eb" stroke-width="4" fill="none"/>
    <text x="200" y="180" font-family="sans-serif" font-size="16" text-anchor="middle">Trend Line</text>
</svg>""",
    "double-top-bottom.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <path d="M50 150 L 120 50 L 200 100 L 280 50 L 350 150" stroke="#dc2626" stroke-width="4" fill="none"/>
    <text x="200" y="180" font-family="sans-serif" font-size="16" text-anchor="middle">Double Top Formation</text>
</svg>""",
    "head-shoulders.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <path d="M50 150 L 120 100 L 150 120 L 200 40 L 250 120 L 280 100 L 350 150" stroke="#dc2626" stroke-width="4" fill="none"/>
    <path d="M100 120 L 300 120" stroke="#1e293b" stroke-width="2" stroke-dasharray="5,5" fill="none"/>
    <text x="200" y="180" font-family="sans-serif" font-size="16" text-anchor="middle">Head &amp; Shoulders</text>
</svg>""",
    "pe-ratio.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <text x="200" y="90" font-family="sans-serif" font-size="24" font-weight="bold" text-anchor="middle">F/K = Fiyat / Kazanç</text>
    <text x="200" y="130" font-family="sans-serif" font-size="14" text-anchor="middle">Price to Earnings Ratio</text>
</svg>""",
    "diversification.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <circle cx="150" cy="100" r="60" fill="#2563eb" opacity="0.8"/>
    <circle cx="200" cy="100" r="50" fill="#16a34a" opacity="0.8"/>
    <circle cx="250" cy="100" r="40" fill="#dc2626" opacity="0.8"/>
    <text x="200" y="180" font-family="sans-serif" font-size="16" text-anchor="middle">Risk Diversification</text>
</svg>""",
    "stop-loss.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <path d="M50 80 L 150 100 L 250 150 L 350 180" stroke="#1e293b" stroke-width="4" fill="none"/>
    <path d="M50 120 L 350 120" stroke="#dc2626" stroke-width="2" stroke-dasharray="5,5" fill="none"/>
    <text x="200" y="110" font-family="sans-serif" font-size="14" fill="#dc2626" text-anchor="middle">Stop-Loss Level</text>
</svg>""",
    "kap.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
    <rect width="400" height="200" fill="#f8fafc"/>
    <rect x="100" y="50" width="200" height="100" fill="#2563eb" rx="10"/>
    <text x="200" y="110" font-family="sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle">KAP</text>
    <text x="200" y="180" font-family="sans-serif" font-size="14" text-anchor="middle">Public Disclosure Platform</text>
</svg>"""
}

for filename, content in SVGS.items():
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"Created {filename}")

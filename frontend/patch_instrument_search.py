from pathlib import Path
import re
p = Path('frontend/components/InstrumentSearch.tsx')
c = p.read_text('utf-8')
c = re.sub(r'placeholder="[^"]+"', 'placeholder="Sembol veya Varlık Ara (örn. THYAO, AAPL, GLDTR)"', c)
p.write_text(c, 'utf-8')
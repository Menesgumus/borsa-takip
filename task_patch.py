from pathlib import Path
import re

path = Path(r'C:\Users\muham\.gemini\antigravity\brain\94bb8024-3a82-4e6c-ae7f-6872bb131b2a\task.md')
content = path.read_text(encoding='utf-8')

content = content.replace(
    '- [ ] Update ackend/app/schemas/instrument.py to include AssetClass enum',
    '- [x] Update ackend/app/schemas/instrument.py to include AssetClass enum'
).replace(
    '- [ ] Update ackend/app/db/models.py for Instrument',
    '- [x] Update ackend/app/db/models.py for Instrument'
).replace(
    '- [ ] Create and test Alembic migration',
    '- [x] Create and test Alembic migration'
).replace(
    '- [ ] Update ackend/scripts/seed_qa_instruments.py',
    '- [x] Update ackend/scripts/seed_qa_instruments.py'
).replace(
    '- [ ] Create ackend/app/services/fx_service.py',
    '- [x] Create ackend/app/services/fx_service.py'
).replace(
    '- [ ] Create ackend/app/schemas/portfolio.py DTOs',
    '- [x] Create ackend/app/schemas/portfolio.py DTOs'
).replace(
    '- [ ] Create ackend/app/services/allocation_service.py. Implement multi-asset valuation, target weights, positive deficit distribution, whole-share math, and 30% limit checks.',
    '- [x] Create ackend/app/services/allocation_service.py. Implement multi-asset valuation, target weights, positive deficit distribution, whole-share math, and 30% limit checks.'
).replace(
    '- [ ] Implement POST /api/v1/portfolios/{id}/basket-preview in ackend/app/api/endpoints/portfolios.py.',
    '- [x] Implement POST /api/v1/portfolios/{id}/basket-preview in ackend/app/api/endpoints/portfolios.py.'
).replace(
    '- [ ] Implement POST /api/v1/portfolios/{id}/execution-preview.',
    '- [x] Implement POST /api/v1/portfolios/{id}/execution-preview.'
).replace(
    '- [ ] Implement POST /api/v1/portfolios/{id}/manual-trade for REAL portfolios.',
    '- [x] Implement POST /api/v1/portfolios/{id}/manual-trade for REAL portfolios.'
).replace(
    '- [ ] Add AssetClass and multi-currency fields to rontend/types/.',
    '- [x] Add AssetClass and multi-currency fields to rontend/lib/types.ts.'
).replace(
    '- [ ] Add ormatMoney(value, currency) utility.',
    '- [x] Add ormatMoney(value, currency) utility.'
).replace(
    '- [ ] Update rontend/app/(protected)/portfolios/[id]/page.tsx with allocation summary and multi-currency table columns.',
    '- [x] Update rontend/app/(protected)/portfolios/[id]/page.tsx with allocation summary and multi-currency table columns.'
)

path.write_text(content, encoding='utf-8')
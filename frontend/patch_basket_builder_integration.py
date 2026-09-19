from pathlib import Path
p = Path('frontend/app/(protected)/portfolios/[id]/page.tsx')
c = p.read_text('utf-8')
c = c.replace('import { DataStateBadge } from "@/components/DataStateBadge";', 'import { DataStateBadge } from "@/components/DataStateBadge";\nimport { BasketBuilder } from "@/components/BasketBuilder";')
c = c.replace('Sepet oluşturma arayüzü yapım aşamasındadır.', '<BasketBuilder portfolioId={id} />')
p.write_text(c, 'utf-8')
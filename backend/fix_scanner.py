from pathlib import Path

# 1. Fix Basket Service
path = Path('app/services/basket_service.py')
content = path.read_text(encoding='utf-8')

content = content.replace('from app.services.scanner import ScannerService', 'from app.services.scanner import scan_opportunities\nfrom app.db.models import User')
content = content.replace(
'''        # Get actionable opportunities
        scanner = ScannerService(self.registry)
        opportunities = await scanner.scan_market(db)''',
'''        # Get actionable opportunities
        # We need a User object for scan_opportunities, but we have user_profile.
        user = await db.scalar(select(User).where(User.id == user_profile.id))
        opportunities = await scan_opportunities(db, user, portfolio_id)'''
)
path.write_text(content, encoding='utf-8')

# 2. Fix Portfolios Endpoints
path = Path('app/api/v1/endpoints/portfolios.py')
content = path.read_text(encoding='utf-8')
content = content.replace(
'''    from app.services.scanner import ScannerService
    scanner = ScannerService(registry)
    opps = await scanner.scan_market(db)''',
'''    from app.services.scanner import scan_opportunities
    opps = await scan_opportunities(db, current_user, portfolio_id)'''
)
path.write_text(content, encoding='utf-8')

from fastapi import APIRouter

from app.api.v1.endpoints import (
    test_fixtures,
    alerts,
    auth,
    backtests,
    behavior,
    chat,
    education,
    instruments,
    lifecycle,
    opportunities,
    outcomes,
    portfolios,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(instruments.router, prefix="/instruments", tags=["instruments"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
api_router.include_router(behavior.router, prefix="/behavior", tags=["behavior"])
api_router.include_router(lifecycle.router, prefix="/portfolios/{portfolio_id}/lifecycle", tags=["lifecycle"])

api_router.include_router(test_fixtures.router, prefix="/test-fixtures", tags=["test_fixtures"])

import asyncio
import os
import sys

# Set up paths and env variables
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Portfolio, PortfolioType, Instrument, User, ProviderMapping, InstrumentType, PortfolioTransaction
from app.db.session import async_session_maker
from app.main import app

async def main():
    async with async_session_maker() as db_session:
        # Just grab the first user and portfolio
        user = (await db_session.execute(select(User))).scalars().first()
        portfolio = (await db_session.execute(select(Portfolio).where(Portfolio.user_id == user.id))).scalars().first()
        
        if not portfolio:
            print("No portfolio found.")
            return

        print(f"Testing portfolio {portfolio.id} for user {user.id}")

    from app.api.v1.endpoints.auth import get_current_user
    async def override_get_current_user():
        return user
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(f"/api/v1/portfolios/{portfolio.id}/transactions")
        print("Status code:", res.status_code)
        print("Response:", res.json())

if __name__ == "__main__":
    asyncio.run(main())

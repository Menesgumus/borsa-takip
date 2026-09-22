import re

with open("backend/app/api/v1/endpoints/portfolios.py", "r", encoding="utf-8") as f:
    content = f.read()

# Imports
if "from fastapi import APIRouter" in content and "Header" not in content:
    content = content.replace("from fastapi import APIRouter, Depends, HTTPException", "from fastapi import APIRouter, Depends, HTTPException, Header")
if "check_and_record_idempotency" not in content:
    content = "from app.services.idempotency import check_and_record_idempotency, build_idempotency_record\n" + content

# Patch create_transaction
content = content.replace(
"""async def create_transaction(
    portfolio_id: int,
    tx_in: TransactionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:""",
"""async def create_transaction(
    portfolio_id: int,
    tx_in: TransactionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    x_idempotency_key: str = Header(default=None)
) -> Any:"""
)

# Patch execute_trade
content = content.replace(
"""async def execute_trade(
    portfolio_id: int,
    trade_in: PortfolioTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:""",
"""async def execute_trade(
    portfolio_id: int,
    trade_in: PortfolioTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    x_idempotency_key: str = Header(default=None)
) -> Any:"""
)

# Patch execute_manual_trade
content = content.replace(
"""async def execute_manual_trade(
    portfolio_id: int,
    trade_in: ManualTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:""",
"""async def execute_manual_trade(
    portfolio_id: int,
    trade_in: ManualTradeCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    x_idempotency_key: str = Header(default=None)
) -> Any:"""
)

with open("backend/app/api/v1/endpoints/portfolios.py", "w", encoding="utf-8") as f:
    f.write(content)

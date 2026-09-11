from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Instrument, Portfolio, PortfolioTransaction
from app.market.dto import QuoteDTO
from app.market.exceptions import ProviderUnavailableError
from app.market.registry import registry
from app.services.portfolio_ledger import PortfolioState, TransactionData, fold_transactions
from app.services.provider_resolver import resolve_provider


@dataclass
class ValuationResult:
    cash_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal | None
    total_market_value: Decimal | None
    invested_market_value: Decimal | None
    positions: list[dict] # Will map to PositionDTO
    data_freshness: str
    valuation_complete: bool

def calculate_portfolio_valuation(
    state: PortfolioState,
    instruments: dict[int, Instrument],
    quotes: dict[int, QuoteDTO]
) -> ValuationResult:
    total_unrealized_pnl = Decimal("0")
    invested_market_value = Decimal("0")
    valuation_complete = True
    data_freshness = "LIVE"

    evaluated_positions = []

    for inst_id, pos in state.positions.items():
        if pos.quantity <= 0:
            continue

        instrument = instruments.get(inst_id)
        symbol = instrument.symbol if instrument else "UNKNOWN"
        name = instrument.name if instrument else "Unknown Instrument"

        quote = quotes.get(inst_id)

        current_price = None
        market_value = None
        unrealized_pnl = None
        unrealized_pnl_percent = None

        if quote:
            current_price = quote.price
            market_value = current_price * pos.quantity
            cost_basis = pos.average_cost * pos.quantity
            unrealized_pnl = market_value - cost_basis
            if cost_basis > 0:
                unrealized_pnl_percent = (unrealized_pnl / cost_basis) * 100

            invested_market_value += market_value
            total_unrealized_pnl += unrealized_pnl

            if getattr(quote, 'is_delayed', False) and data_freshness == "LIVE":
                data_freshness = "DELAYED"
            if getattr(quote, 'is_stale', False):
                data_freshness = "STALE"
        else:
            valuation_complete = False

        evaluated_positions.append({
            "instrument_id": inst_id,
            "symbol": symbol,
            "name": name,
            "quantity": pos.quantity,
            "average_cost": pos.average_cost,
            "realized_pnl": pos.realized_pnl,
            "current_price": current_price,
            "market_value": market_value,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_percent": unrealized_pnl_percent
        })

    if not valuation_complete:
        final_unrealized = None
        final_market_value = None
        final_invested = None
    else:
        final_unrealized = total_unrealized_pnl
        final_invested = invested_market_value
        final_market_value = state.cash_balance + invested_market_value

    return ValuationResult(
        cash_balance=state.cash_balance,
        total_deposits=state.total_deposits,
        total_withdrawals=state.total_withdrawals,
        total_realized_pnl=state.total_realized_pnl,
        total_unrealized_pnl=final_unrealized,
        total_market_value=final_market_value,
        invested_market_value=final_invested,
        positions=evaluated_positions,
        data_freshness=data_freshness,
        valuation_complete=valuation_complete
    )

async def evaluate_portfolios(db: AsyncSession, portfolios: Sequence[Portfolio]) -> dict[int, ValuationResult]:
    """Canonical, batched valuation of multiple portfolios in one unified function."""
    if not portfolios:
        return {}

    p_ids = [p.id for p in portfolios]
    all_txs_result = await db.execute(select(PortfolioTransaction).where(PortfolioTransaction.portfolio_id.in_(p_ids)))
    all_txs = all_txs_result.scalars().all()

    txs_by_portfolio = {p.id: [] for p in portfolios}
    for t in all_txs:
        txs_by_portfolio[t.portfolio_id].append(
            TransactionData(
                id=t.id,
                transaction_type=t.transaction_type,
                instrument_id=t.instrument_id,
                quantity=t.quantity,
                price=t.price,
                fee=t.fee,
                executed_at=t.executed_at
            )
        )

    states = {}
    all_inst_ids = set()
    for p in portfolios:
        state = fold_transactions(txs_by_portfolio[p.id])
        states[p.id] = state
        for inst_id, pos in state.positions.items():
            if pos.quantity > 0:
                all_inst_ids.add(inst_id)

    instruments: dict[int, Instrument] = {}
    quotes: dict[int, QuoteDTO] = {}

    if all_inst_ids:
        inst_res = await db.execute(
            select(Instrument)
            .options(selectinload(Instrument.provider_mappings))
            .where(Instrument.id.in_(all_inst_ids))
        )
        for inst in inst_res.scalars().all():
            instruments[int(inst.id)] = inst

        provider_symbols: dict[str, list[str]] = {}
        symbol_to_inst_id: dict[str, int] = {}

        for inst_id, inst in instruments.items():
            try:
                resolved = resolve_provider(inst)
                provider_symbols.setdefault(resolved.provider_name, []).append(resolved.provider_symbol)
                symbol_to_inst_id[f"{resolved.provider_name}:{resolved.provider_symbol}"] = inst_id
            except ProviderUnavailableError:
                pass

        for provider_name, symbols_list in provider_symbols.items():
            try:
                quotes_res = await registry.get_quotes(provider_name, symbols_list)
                for quote in quotes_res:
                    i_id = symbol_to_inst_id.get(f"{provider_name}:{quote.symbol}")
                    if i_id is not None:
                        quotes[i_id] = quote
            except ProviderUnavailableError:
                pass

    results = {}
    for p in portfolios:
        results[int(p.id)] = calculate_portfolio_valuation(states[p.id], instruments, quotes)

    return results

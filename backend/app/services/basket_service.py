import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AssetClass, Portfolio, User, UserProfile
from app.market.registry import MarketDataRegistry
from app.schemas.portfolio import (
    BasketItemDTO,
    BasketPreviewResponse,
    SleeveAllocationDTO,
)
from app.services.allocation_service import AllocationService
from app.services.fx_service import FxRateService
from app.services.portfolio_valuation import evaluate_portfolios
from app.services.scanner import scan_opportunities

logger = logging.getLogger(__name__)

class BasketBuilderService:
    def __init__(self, registry: MarketDataRegistry) -> None:
        self.registry = registry
        self.fx = FxRateService(registry)

    async def build_basket(self, db: AsyncSession, portfolio_id: int, deploy_amount: Decimal, user_profile: UserProfile) -> BasketPreviewResponse:
        # Load portfolio and evaluate
        portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id))
        if not portfolio:
            raise ValueError("Portfolio not found")

        evaluations = await evaluate_portfolios(db, [portfolio])
        valuation = evaluations.get(portfolio_id)

        if not valuation or not valuation.valuation_complete:
            # We can't build a basket if we can't value existing positions
            data_state = "INCOMPLETE"
            valuation_complete = False
        else:
            data_state = valuation.data_freshness
            valuation_complete = True

        cash_balance = valuation.cash_balance if valuation else Decimal("0")
        current_market_value = valuation.invested_market_value if valuation and valuation.invested_market_value else Decimal("0")
        total_value_before_deploy = cash_balance + current_market_value

        # Calculate target cash to preserve based on target weight
        risk_tolerance = user_profile.risk_tolerance if user_profile and user_profile.risk_tolerance else "MEDIUM"
        target_weights = AllocationService.get_target_weights(risk_tolerance)

        target_cash_weight = target_weights.get("CASH", Decimal("0"))
        total_value_after_deploy = total_value_before_deploy + deploy_amount
        target_cash_reserve = total_value_after_deploy * target_cash_weight

        available_cash = cash_balance + deploy_amount

        # Gather all existing positions by asset class
        current_sleeve_values = {
            AssetClass.BIST_EQUITY: Decimal("0"),
            AssetClass.US_EQUITY: Decimal("0"),
            AssetClass.GOLD: Decimal("0"),
        }

        if valuation and valuation.positions:
            for p in valuation.positions:
                ac = p.get("asset_class")
                if ac and ac in current_sleeve_values and p.get("market_value"):
                    current_sleeve_values[ac] += p["market_value"]

        # Calculate deficits and proposed allocations
        sleeves = []
        for ac, target_w in target_weights.items():
            if ac == "CASH":
                continue

            current_v = current_sleeve_values.get(ac, Decimal("0"))
            current_w = (current_v / total_value_before_deploy) if total_value_before_deploy > 0 else Decimal("0")
            target_v = total_value_after_deploy * target_w
            deficit_v = max(Decimal("0"), target_v - current_v)

            sleeves.append({
                "dto": SleeveAllocationDTO(
                    asset_class=str(ac),
                    current_value=current_v,
                    current_weight=current_w,
                    target_weight=target_w,
                    target_value=target_v,
                    deficit_value=deficit_v,
                    proposed_allocation=Decimal("0"),
                    unallocated_reason=None
                ),
                "deficit": deficit_v
            })

        # Get actionable opportunities
        # We need a User object for scan_opportunities, but we have user_profile.
        user = await db.scalar(select(User).where(User.id == user_profile.id))
        opportunities = await scan_opportunities(db, user, portfolio_id)

        # Filter actionable: market_score >= 70, personal_action == BUY
        actionable = [o for o in opportunities if o.personal_action in ("BUY", "STRONG_BUY")]
        actionable.sort(key=lambda x: x.market_score, reverse=True)

        usd_try_rate = await self.fx.get_usd_try_rate(db)
        if usd_try_rate is None:
            usd_try_rate = Decimal("1.0") # Fallback, though valuation should catch it

        basket_items = []
        allocated_total = Decimal("0")

        # We will track current values per instrument to enforce 30% rule
        pos_values = {}
        if valuation and valuation.positions:
            for p in valuation.positions:
                pos_values[p["instrument_id"]] = p.get("market_value", Decimal("0"))

        MAX_POS_WEIGHT = Decimal("0.30")

        for sleeve_dict in sleeves:
            sleeve = sleeve_dict["dto"]
            deficit = sleeve_dict["deficit"]
            ac = sleeve.asset_class

            if deficit <= 0:
                continue

            # Candidates for this sleeve
            candidates = [o for o in actionable if str(o.asset_class) == ac]

            if not candidates:
                sleeve.unallocated_reason = "NO_ACTIONABLE_OPPORTUNITIES"
                continue

            budget_per_candidate = deficit / Decimal(len(candidates))
            sleeve_allocated = Decimal("0")

            for candidate in candidates:
                # Calculate fx
                if candidate.currency == "USD":
                    fx = usd_try_rate
                else:
                    fx = Decimal("1.0")

                analysis_base = candidate.current_price * fx

                # Check 30% limit
                current_pos_val = pos_values.get(candidate.instrument_id, Decimal("0"))
                max_allowed_total_val = total_value_after_deploy * MAX_POS_WEIGHT
                room = max(Decimal("0"), max_allowed_total_val - current_pos_val)

                budget = min(budget_per_candidate, room)

                if budget <= 0 or analysis_base <= 0:
                    continue

                quantity = int(budget // analysis_base)

                if quantity <= 0:
                    continue

                proposed_base = Decimal(quantity) * analysis_base
                proposed_native = Decimal(quantity) * candidate.current_price

                sleeve_allocated += proposed_base
                allocated_total += proposed_base

                basket_items.append(BasketItemDTO(
                    instrument_id=candidate.instrument_id,
                    symbol=candidate.symbol,
                    name=candidate.name,
                    asset_class=ac,
                    native_currency=candidate.currency,
                    market_view=candidate.market_view,
                    personal_action=candidate.personal_action,
                    market_score=candidate.market_score,
                    data_quality_score=candidate.data_quality_score,
                    analysis_native_price=candidate.current_price,
                    fx_rate_to_base=fx,
                    analysis_base_price=analysis_base,
                    proposed_quantity=Decimal(quantity),
                    proposed_native_budget=proposed_native,
                    proposed_base_budget=proposed_base,
                    projected_weight=(current_pos_val + proposed_base) / total_value_after_deploy,
                    recommended_target_weight=budget_per_candidate / total_value_after_deploy,
                    hard_max_weight=MAX_POS_WEIGHT,
                    sizing_state="OK",
                    reason_codes=[]
                ))

            sleeve.proposed_allocation = sleeve_allocated

        final_sleeves = [s["dto"] for s in sleeves]
        unallocated = deploy_amount - allocated_total

        return BasketPreviewResponse(
            portfolio_id=portfolio_id,
            base_currency="TRY",
            risk_tolerance=risk_tolerance,
            allocation_policy_version="v1",
            portfolio_total_value=total_value_before_deploy,
            available_cash=available_cash,
            requested_deploy_amount=deploy_amount,
            allocated_amount=allocated_total,
            unallocated_amount=unallocated,
            target_cash_reserve=target_cash_reserve,
            constraint_unallocated=unallocated,
            valuation_complete=valuation_complete,
            data_state=data_state,
            sleeves=final_sleeves,
            items=basket_items
        )

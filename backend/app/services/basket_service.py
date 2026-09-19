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
            data_state = "INCOMPLETE"
            valuation_complete = False
        else:
            data_state = valuation.data_freshness
            valuation_complete = True

        usd_try_rate_result = await self.fx.get_usd_try_rate(db)
        if usd_try_rate_result:
            usd_try_rate = usd_try_rate_result.rate
        else:
            usd_try_rate = None
            valuation_complete = False
            data_state = "INCOMPLETE"

        cash_balance = valuation.cash_balance if valuation else Decimal("0")
        current_market_value = valuation.invested_market_value if valuation and valuation.invested_market_value else Decimal("0")
        total_portfolio_value = cash_balance + current_market_value

        # Calculate target cash to preserve
        risk_tolerance = user_profile.risk_tolerance if user_profile and user_profile.risk_tolerance else "MEDIUM"
        target_weights = AllocationService.get_target_weights(risk_tolerance)

        target_cash_weight = target_weights.get("CASH", Decimal("0"))
        target_cash_reserve = total_portfolio_value * target_cash_weight
        minimum_cash_to_keep = max(target_cash_reserve, Decimal("0"))

        deployable_cash_under_policy = max(Decimal("0"), cash_balance - minimum_cash_to_keep)

        if deploy_amount == 0:
            deploy_amount = cash_balance
            
        # Enforce validation: deploy_amount <= available_cash
        if deploy_amount > cash_balance:
            raise ValueError("Requested deploy amount exceeds available cash")
        if deploy_amount < 0:
            raise ValueError("Deploy amount must be >= 0")

        actual_maximum_deployment = min(deploy_amount, deployable_cash_under_policy)
        remaining_deploy = actual_maximum_deployment

        # Gather all existing positions by asset class
        current_sleeve_values = {
            str(AssetClass.BIST_EQUITY): Decimal("0"),
            str(AssetClass.US_EQUITY): Decimal("0"),
            str(AssetClass.GOLD): Decimal("0"),
        }

        if valuation and valuation.positions:
            for p in valuation.positions:
                ac = p.get("asset_class")
                if ac and ac in current_sleeve_values and p.get("market_value"):
                    current_sleeve_values[ac] += p["market_value"]

        # Calculate deficits
        sleeves = []
        for ac, target_w in target_weights.items():
            if ac == "CASH":
                continue

            current_v = current_sleeve_values.get(ac, Decimal("0"))
            current_w = (current_v / total_portfolio_value) if total_portfolio_value > 0 else Decimal("0")
            target_v = total_portfolio_value * target_w
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

        user = await db.scalar(select(User).where(User.id == user_profile.user_id))
        opportunities = await scan_opportunities(db, user, portfolio_id)

        # Candidate Eligibility
        actionable = []
        for o in opportunities:
            if o.asset_class == AssetClass.FX_REFERENCE:
                continue
            action = o.personal_action or o.market_view
            if action not in ("BUY", "STRONG_BUY"):
                continue
            if o.sizing_state != "OK":
                continue
            if getattr(o, "missing_data", False):
                continue
            if getattr(o, "data_quality_score", 0) < 50:
                continue
            quote_price = getattr(o, "quote_price", getattr(o, "current_price", Decimal("0")))
            if quote_price <= 0:
                continue

            currency = getattr(o, "currency", "TRY")
            if currency == "USD" and usd_try_rate is None:
                continue

            if getattr(o, "max_executable_quantity", Decimal("1")) <= 0:
                continue

            actionable.append(o)

        actionable.sort(key=lambda x: getattr(x, "market_score", 0), reverse=True)

        basket_items = []
        allocated_total = Decimal("0")

        pos_values = {}
        if valuation and valuation.positions:
            for p in valuation.positions:
                pos_values[p["instrument_id"]] = p.get("market_value", Decimal("0"))

        max_pos_weight = Decimal("0.30")

        for sleeve_dict in sleeves:
            sleeve = sleeve_dict["dto"]
            deficit = sleeve_dict.get("deficit", Decimal("0"))
            if not isinstance(deficit, Decimal):
                deficit = Decimal(str(deficit))
            ac = sleeve.asset_class

            if deficit <= Decimal("0"):
                sleeve.unallocated_reason = "TARGET_REACHED"
                continue

            candidates = [o for o in actionable if str(o.asset_class) == ac]

            if not candidates:
                sleeve.unallocated_reason = "NO_ACTIONABLE_OPPORTUNITIES"
                continue

            budget_per_candidate = deficit / Decimal(len(candidates))
            sleeve_allocated = Decimal("0")

            for candidate in candidates:
                if remaining_deploy <= 0:
                    break

                currency = getattr(candidate, "currency", "TRY")
                fx = usd_try_rate if currency == "USD" and usd_try_rate is not None else Decimal("1.0")

                quote_price = getattr(candidate, "quote_price", getattr(candidate, "current_price", Decimal("0")))
                analysis_base = quote_price * fx

                current_pos_val = pos_values.get(candidate.instrument_id, Decimal("0"))
                max_allowed_total_val = total_portfolio_value * max_pos_weight
                room = max(Decimal("0"), max_allowed_total_val - current_pos_val)

                # Respect sizing capacity
                sizing_max_budget = getattr(candidate, "max_executable_budget", Decimal("Infinity"))

                budget = min(budget_per_candidate, room, remaining_deploy, sizing_max_budget)

                if budget <= 0 or analysis_base <= 0:
                    continue

                quantity = int(budget // analysis_base)

                if quantity <= 0:
                    continue

                # Respect max executable quantity from sizing
                sizing_max_quantity = getattr(candidate, "max_executable_quantity", Decimal("Infinity"))
                quantity = int(min(Decimal(quantity), sizing_max_quantity))

                proposed_base = Decimal(quantity) * analysis_base
                proposed_native = Decimal(quantity) * quote_price

                sleeve_allocated += proposed_base
                allocated_total += proposed_base
                remaining_deploy -= proposed_base

                basket_items.append(BasketItemDTO(
                    instrument_id=candidate.instrument_id,
                    symbol=candidate.symbol,
                    name=candidate.name,
                    asset_class=ac,
                    native_currency=currency,
                    market_view=candidate.market_view,
                    personal_action=candidate.personal_action,
                    market_score=getattr(candidate, "market_score", 0),
                    data_quality_score=getattr(candidate, "data_quality_score", 0),
                    analysis_native_price=quote_price,
                    fx_rate_to_base=fx,
                    analysis_base_price=analysis_base,
                    proposed_quantity=Decimal(quantity),
                    proposed_native_budget=proposed_native,
                    proposed_base_budget=proposed_base,
                    projected_weight=(current_pos_val + proposed_base) / total_portfolio_value,
                    recommended_target_weight=budget_per_candidate / total_portfolio_value,
                    hard_max_weight=max_pos_weight,
                    sizing_state="OK",
                    reason_codes=[]
                ))

            sleeve.proposed_allocation = sleeve_allocated

        final_sleeves = [s["dto"] for s in sleeves]
        unallocated_from_deploy = deploy_amount - allocated_total

        return BasketPreviewResponse(
            portfolio_id=portfolio_id,
            base_currency="TRY",
            risk_tolerance=risk_tolerance,
            allocation_policy_version="v1",
            portfolio_total_value=total_portfolio_value,
            available_cash=cash_balance,
            requested_deploy_amount=deploy_amount,
            allocated_amount=allocated_total,
            unallocated_amount=unallocated_from_deploy,
            target_cash_reserve=target_cash_reserve,
            constraint_unallocated=deploy_amount - actual_maximum_deployment,
            valuation_complete=valuation_complete,
            data_state=data_state,
            sleeves=final_sleeves,
            items=basket_items
        )

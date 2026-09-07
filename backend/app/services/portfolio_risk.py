from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from app.services.portfolio_ledger import PortfolioState, TransactionType
from app.schemas.risk import PortfolioRiskMetrics, PositionExposure, LimitViolation

# Configuration for risk limits
MAX_SINGLE_POSITION_WEIGHT = Decimal("0.30") # 30%

def calculate_historical_var(returns: List[Decimal], confidence_level: Decimal = Decimal("0.95")) -> Optional[Decimal]:
    if len(returns) < 30: # Need at least 30 observations for meaningful VaR
        return None
    sorted_returns = sorted(returns)
    index = int((Decimal("1") - confidence_level) * len(sorted_returns))
    # Return as a positive loss magnitude
    return -sorted_returns[index] if sorted_returns[index] < 0 else Decimal("0")

def calculate_portfolio_risk(
    state: PortfolioState, 
    current_prices: Dict[int, Decimal],
    symbols: Dict[int, str],
    historical_returns_aligned: Optional[List[Decimal]] = None,
    drawdown: Optional[Decimal] = None,
    volatility: Optional[Decimal] = None
) -> PortfolioRiskMetrics:
    
    invested_exposure = Decimal("0")
    positions_exposure = []
    
    # Calculate coverage
    total_cost_basis = sum(pos.quantity * pos.average_cost for pos in state.positions.values())
    covered_cost_basis = Decimal("0")
    
    for inst_id, pos in state.positions.items():
        if pos.quantity <= Decimal("0"):
            continue
            
        price = current_prices.get(inst_id)
        if price is not None:
            market_value = pos.quantity * price
            invested_exposure += market_value
            covered_cost_basis += (pos.quantity * pos.average_cost)
            positions_exposure.append(PositionExposure(
                instrument_id=inst_id,
                symbol=symbols.get(inst_id, str(inst_id)),
                weight_percentage=Decimal("0"), # calculated later
                market_value=market_value,
                is_stale=False
            ))
        else:
            # Stale
            positions_exposure.append(PositionExposure(
                instrument_id=inst_id,
                symbol=symbols.get(inst_id, str(inst_id)),
                weight_percentage=Decimal("0"),
                market_value=Decimal("0"), # do not interpret as zero, just skipped from total
                is_stale=True
            ))

    total_market_value = invested_exposure + state.cash_balance
    
    # Calculate weights
    for exp in positions_exposure:
        if not exp.is_stale and total_market_value > Decimal("0"):
            exp.weight_percentage = (exp.market_value / total_market_value) * Decimal("100")
            
    cash_weight = (state.cash_balance / total_market_value) * Decimal("100") if total_market_value > Decimal("0") else Decimal("0")
    invested_weight = (invested_exposure / total_market_value) * Decimal("100") if total_market_value > Decimal("0") else Decimal("0")
    
    # Check limits
    violations = []
    for exp in positions_exposure:
        if exp.weight_percentage > (MAX_SINGLE_POSITION_WEIGHT * Decimal("100")):
            violations.append(LimitViolation(
                rule_name="MAX_SINGLE_POSITION_WEIGHT",
                limit_value=MAX_SINGLE_POSITION_WEIGHT * Decimal("100"),
                actual_value=exp.weight_percentage,
                reason_code="POSITION_CONCENTRATION_LIMIT_EXCEEDED"
            ))

    coverage = (covered_cost_basis / total_cost_basis * Decimal("100")) if total_cost_basis > Decimal("0") else Decimal("100")
    is_stale = any(exp.is_stale for exp in positions_exposure)
    
    var_95_1d = None
    if historical_returns_aligned is not None:
        var_95_1d = calculate_historical_var(historical_returns_aligned, Decimal("0.95"))
        if var_95_1d is not None and total_market_value > Decimal("0"):
             # Convert percentage var to absolute loss magnitude
             var_95_1d = var_95_1d * total_market_value
             
    return PortfolioRiskMetrics(
        portfolio_id=0, # to be filled by caller
        total_market_value=total_market_value,
        invested_exposure=invested_exposure,
        cash_exposure=state.cash_balance,
        cash_weight_percentage=cash_weight,
        invested_weight_percentage=invested_weight,
        historical_var_95_1d=var_95_1d,
        annualized_volatility=volatility,
        max_drawdown=drawdown,
        positions_exposure=positions_exposure,
        limit_violations=violations,
        calculated_at=datetime.now(timezone.utc),
        data_freshness="STALE" if is_stale else "LIVE",
        coverage_percentage=coverage
    )
from app.services.portfolio_ledger import fold_transactions, TransactionData
from app.schemas.risk import WhatIfResponse
from copy import deepcopy

def simulate_what_if(
    ledger_transactions: List[TransactionData],
    simulated_tx: TransactionData,
    current_prices: Dict[int, Decimal],
    symbols: Dict[int, str],
    historical_returns: Optional[List[Decimal]] = None
) -> WhatIfResponse:
    
    # Base risk
    base_state = fold_transactions(ledger_transactions)
    base_risk = calculate_portfolio_risk(base_state, current_prices, symbols, historical_returns)
    
    # Simulated risk
    sim_ledger = list(ledger_transactions) + [simulated_tx]
    sim_state = fold_transactions(sim_ledger)
    sim_risk = calculate_portfolio_risk(sim_state, current_prices, symbols, historical_returns)
    
    # Deltas
    base_var = base_risk.historical_var_95_1d or Decimal("0")
    sim_var = sim_risk.historical_var_95_1d or Decimal("0")
    delta_var = sim_var - base_var if (base_risk.historical_var_95_1d is not None and sim_risk.historical_var_95_1d is not None) else None
    
    delta_invested = sim_risk.invested_exposure - base_risk.invested_exposure
    
    base_violations = {v.reason_code: v for v in base_risk.limit_violations}
    sim_violations = {v.reason_code: v for v in sim_risk.limit_violations}
    
    newly_triggered = [v for code, v in sim_violations.items() if code not in base_violations]
    resolved = [v for code, v in base_violations.items() if code not in sim_violations]
    
    return WhatIfResponse(
        before_risk=base_risk,
        after_risk=sim_risk,
        delta_var_95_1d=delta_var,
        delta_invested_exposure=delta_invested,
        newly_triggered_limits=newly_triggered,
        resolved_limits=resolved
    )

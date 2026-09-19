from pathlib import Path

content = Path('backend/app/services/basket_service.py').read_text(encoding='utf-8')

# We need to import scanner and get actionable opportunities.
new_imports = '''from app.market.registry import MarketDataRegistry
from app.services.scanner import ScannerService'''

content = content.replace('from app.market.registry import MarketDataRegistry', new_imports)

# Replace the end of build_basket with the allocation logic
logic = '''            sleeves.append(SleeveAllocationDTO(
                asset_class=str(ac),
                current_value=current_v,
                current_weight=current_w,
                target_weight=target_w,
                target_value=target_v,
                deficit_value=deficit_v,
                proposed_allocation=Decimal("0"),
                unallocated_reason=None
            ))
            
        return BasketPreviewResponse('''

new_logic = '''            sleeves.append({
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
        scanner = ScannerService(self.registry)
        opportunities = await scanner.scan_market(db)
        
        # Filter actionable: market_score >= 70, personal_action == BUY
        actionable = [o for o in opportunities if o.market_score >= 70 and o.personal_action == "BUY"]
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
            
        return BasketPreviewResponse('''

content = content.replace(logic, new_logic)

Path('backend/app/services/basket_service.py').write_text(content, encoding='utf-8')

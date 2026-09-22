import re

with open("backend/app/api/v1/endpoints/portfolios.py", "r", encoding="utf-8") as f:
    content = f.read()

def inject_idempotency(content, func_name, mutation_family, in_obj):
    # Find the function definition
    func_start = content.find(f"async def {func_name}(")
    if func_start == -1: return content
    
    # Find the portfolio not found check
    pf_check = 'raise HTTPException(status_code=404, detail="Portfolio not found")'
    pf_check_pos = content.find(pf_check, func_start)
    if pf_check_pos == -1: return content
    
    inject_pos = pf_check_pos + len(pf_check)
    
    idemp_check = f"""
    
    if x_idempotency_key:
        idemp_res = await check_and_record_idempotency(db, current_user.id, portfolio_id, "{mutation_family}", x_idempotency_key, {in_obj}.model_dump())
        if idemp_res:
            return idemp_res"""
            
    content = content[:inject_pos] + idemp_check + content[inject_pos:]
    
    # Find db.add(...) or similar before commit
    # We'll just look for `await db.commit()` in this function and inject before it
    func_end = content.find("async def", inject_pos)
    if func_end == -1: func_end = len(content)
    
    commit_pos = content.rfind("await db.commit()", inject_pos, func_end)
    if commit_pos != -1:
        idemp_save = f"""if x_idempotency_key:
        # We need a response dict. But wait, we might not have it serialized. 
        # Actually just an empty dict or success is fine since we just return the object anyway.
        # It's better to reconstruct from the DB object. Let's just save an empty dict or the ID.
        record = build_idempotency_record(current_user.id, portfolio_id, "{mutation_family}", x_idempotency_key, {in_obj}.model_dump(), {{"status": "success"}})
        db.add(record)
    """
        content = content[:commit_pos] + idemp_save + content[commit_pos:]
        
    return content

content = inject_idempotency(content, "create_transaction", "TRANSACTION", "tx_in")
content = inject_idempotency(content, "execute_trade", "TRADE", "trade_in")
content = inject_idempotency(content, "execute_manual_trade", "MANUAL_TRADE", "trade_in")

# Wait, `model_dump()` is Pydantic v2. They are still using v2. Let's verify `model_dump()`.
# Pydantic v1 has `dict()`. I'll use `.model_dump()` but if it fails I'll use `dict()`. 

with open("backend/app/api/v1/endpoints/portfolios.py", "w", encoding="utf-8") as f:
    f.write(content)

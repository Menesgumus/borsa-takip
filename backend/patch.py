content = open('app/api/v1/endpoints/instruments.py', encoding='utf-8').read()
new_endpoint = '''
@router.get("/quotes/batch", response_model=dict[str, QuoteDTO])
async def get_instrument_quotes_batch(
    symbols: str = Query(..., description="Comma separated symbols"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    symbol_list = [s.strip() for s in symbols.split(',')]
    res = await db.execute(
        select(Instrument)
        .options(selectinload(Instrument.provider_mappings))
        .where(Instrument.symbol.in_(symbol_list), Instrument.is_active.is_(True))
    )
    instruments = res.scalars().all()
    
    # Group by provider
    from collections import defaultdict
    by_provider = defaultdict(list)
    symbol_map = {} # provider_symbol -> native_symbol
    
    for inst in instruments:
        provider_name = inst.provider or "yahoo"
        mapping = next((m for m in inst.provider_mappings if m.provider_name == provider_name), None)
        provider_symbol = str(mapping.provider_symbol) if mapping else (inst.symbol + ".IS" if provider_name == "yahoo" and not inst.symbol.endswith(".IS") else inst.symbol)
        by_provider[provider_name].append(provider_symbol)
        symbol_map[provider_symbol] = inst.symbol

    results = {}
    for provider, p_symbols in by_provider.items():
        try:
            quotes = await registry.get_quotes(provider, p_symbols)
            for q in quotes:
                native_symbol = symbol_map.get(q.symbol, q.symbol)
                results[native_symbol] = q
        except Exception:
            pass
            
    return results

'''
content = content.replace('@router.get("/{symbol}/quote",', new_endpoint + '@router.get("/{symbol}/quote",')
open('app/api/v1/endpoints/instruments.py', 'w', encoding='utf-8').write(content)

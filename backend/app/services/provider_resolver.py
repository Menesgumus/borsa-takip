"""Canonical provider resolver - single source of truth for instrument -> provider mapping.

Rules:
1. Primary mapping (is_primary=True) wins.
2. Fallback: lowest priority number.
3. No mapping -> raises ProviderUnavailableError.
4. NEVER silently falls back to mock provider in real runtime.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.db.models import Instrument
from app.market.exceptions import ProviderUnavailableError


@dataclass(frozen=True)
class ResolvedProvider:
    provider_name: str
    provider_symbol: str


def resolve_provider(instrument: Instrument) -> ResolvedProvider:
    """Resolve the canonical provider and provider symbol for an instrument.

    Args:
        instrument: Instrument ORM object with provider_mappings eagerly loaded.

    Returns:
        ResolvedProvider with provider_name and provider_symbol.

    Raises:
        ProviderUnavailableError: If no provider mapping is configured.
    """
    mappings = list(instrument.provider_mappings)

    if not mappings:
        raise ProviderUnavailableError(
            "none",
            f"No provider mapping configured for instrument {instrument.symbol!r}",
        )

    # Primary mapping wins unconditionally
    primary = next((m for m in mappings if m.is_primary), None)
    if primary:
        return ResolvedProvider(
            provider_name=str(primary.provider_name),
            provider_symbol=str(primary.provider_symbol),
        )

    # Fallback: lowest priority number (smaller = higher priority)
    best = sorted(mappings, key=lambda m: (m.priority if m.priority is not None else 999))[0]
    return ResolvedProvider(
        provider_name=str(best.provider_name),
        provider_symbol=str(best.provider_symbol),
    )

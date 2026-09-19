import logging
from decimal import Decimal

from app.db.models import AssetClass

logger = logging.getLogger(__name__)

ALLOCATION_POLICY_VERSION = "v1"

# The agreed allocation targets
ALLOCATION_POLICIES = {
    "LOW": {
        AssetClass.BIST_EQUITY: Decimal("0.15"),
        AssetClass.US_EQUITY: Decimal("0.10"),
        AssetClass.GOLD: Decimal("0.35"),
        "CASH": Decimal("0.40"),
    },
    "MEDIUM": {
        AssetClass.BIST_EQUITY: Decimal("0.30"),
        AssetClass.US_EQUITY: Decimal("0.30"),
        AssetClass.GOLD: Decimal("0.25"),
        "CASH": Decimal("0.15"),
    },
    "HIGH": {
        AssetClass.BIST_EQUITY: Decimal("0.45"),
        AssetClass.US_EQUITY: Decimal("0.45"),
        AssetClass.GOLD: Decimal("0.10"),
        "CASH": Decimal("0.00"),
    }
}

class AllocationService:
    @staticmethod
    def get_target_weights(risk_tolerance: str) -> dict[str | AssetClass, Decimal]:
        return ALLOCATION_POLICIES.get(risk_tolerance.upper(), ALLOCATION_POLICIES["MEDIUM"])

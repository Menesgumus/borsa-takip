import math
from decimal import Decimal


def calculate_reduce_quantity(current_quantity: Decimal, reduce_fraction: Decimal) -> Decimal:
    """
    Deterministic, pure reduce-quantity helper.

    Rules:
      - Whole shares only (floor semantics)
      - 1-share position: 0 executable partial reduction (position can only exit fully)
      - reduce_fraction must be [0, 1)

    Examples:
      qty 10, fraction 0.25 -> 2
      qty 10, fraction 0.50 -> 5
      qty 10, fraction 0.75 -> 7
      qty  1, fraction any  -> 0
    """
    if current_quantity <= Decimal("1"):
        return Decimal("0")
    raw = float(current_quantity) * float(reduce_fraction)
    result = Decimal(math.floor(raw))
    # Clamp: cannot reduce to 0 or negative (use EXIT for that)
    if result <= Decimal("0"):
        return Decimal("0")
    return result

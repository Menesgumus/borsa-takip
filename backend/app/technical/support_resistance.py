from dataclasses import dataclass


@dataclass
class SRLevel:
    price: float
    type: str  # "SUPPORT" or "RESISTANCE"
    strength: int  # Number of touches/pivots clustered into this level

def find_pivots(highs: list[float], lows: list[float], window: int = 5) -> tuple[list[float], list[float]]:
    """
    Find local maxima (resistance pivots) and local minima (support pivots).
    Requires a point to be strictly >= all points in the window before and after it.
    """
    supports: list[float] = []
    resistances: list[float] = []

    n = len(highs)
    if n < window * 2 + 1:
        return supports, resistances

    for i in range(window, n - window):
        is_resistance = True
        is_support = True

        # Check window
        for j in range(1, window + 1):
            if highs[i] <= highs[i - j] or highs[i] < highs[i + j]:
                is_resistance = False
            if lows[i] >= lows[i - j] or lows[i] > lows[i + j]:
                is_support = False

            if not is_resistance and not is_support:
                break

        if is_resistance:
            resistances.append(highs[i])
        if is_support:
            supports.append(lows[i])

    return supports, resistances

def cluster_levels(levels: list[float], threshold_pct: float = 1.5) -> list[SRLevel]:
    """
    Cluster price levels that are within threshold_pct of each other.
    Returns the average price of each cluster and the number of merged points (strength).
    """
    if not levels:
        return []

    sorted_levels = sorted(levels)
    clusters: list[SRLevel] = []

    current_cluster_sum = sorted_levels[0]
    current_cluster_count = 1

    for i in range(1, len(sorted_levels)):
        price = sorted_levels[i]
        avg_price = current_cluster_sum / current_cluster_count

        # Check percentage difference from the average of the current cluster
        pct_diff = abs(price - avg_price) / avg_price * 100

        if pct_diff <= threshold_pct:
            current_cluster_sum += price
            current_cluster_count += 1
        else:
            clusters.append(SRLevel(
                price=current_cluster_sum / current_cluster_count,
                type="",  # set by caller
                strength=current_cluster_count
            ))
            current_cluster_sum = price
            current_cluster_count = 1

    clusters.append(SRLevel(
        price=current_cluster_sum / current_cluster_count,
        type="",
        strength=current_cluster_count
    ))

    return clusters

def calculate_support_resistance(highs: list[float], lows: list[float], window: int = 5, cluster_threshold_pct: float = 1.5) -> list[SRLevel]:
    """
    Detect support and resistance levels from OHLC data.
    """
    supports, resistances = find_pivots(highs, lows, window)

    # Cluster and format
    support_clusters = cluster_levels(supports, cluster_threshold_pct)
    for c in support_clusters:
        c.type = "SUPPORT"

    resistance_clusters = cluster_levels(resistances, cluster_threshold_pct)
    for c in resistance_clusters:
        c.type = "RESISTANCE"

    # Merge both and sort by price
    result = support_clusters + resistance_clusters
    result.sort(key=lambda x: x.price)

    return result

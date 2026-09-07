from dataclasses import dataclass


@dataclass
class PatternResult:
    pattern_name: str
    index: int  # The index in the data where the pattern completes/triggers
    confidence: float  # 0.0 to 1.0
    evidence: str

def detect_doji(opens: list[float], highs: list[float], lows: list[float], closes: list[float]) -> list[PatternResult]:
    results: list[PatternResult] = []
    for i in range(len(opens)):
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        body = abs(o - c)
        range_ = h - l

        if range_ == 0:
            continue

        if body / range_ <= 0.1:  # Body is very small compared to range
            results.append(PatternResult("Doji", i, 0.8, "Small body compared to full candle range"))

    return results

def detect_engulfing(opens: list[float], highs: list[float], lows: list[float], closes: list[float]) -> list[PatternResult]:
    results: list[PatternResult] = []
    for i in range(1, len(opens)):
        prev_o, prev_c = opens[i-1], closes[i-1]
        curr_o, curr_c = opens[i], closes[i]

        prev_body = abs(prev_o - prev_c)
        curr_body = abs(curr_o - curr_c)

        # Bullish Engulfing
        if prev_c < prev_o and curr_c > curr_o:
            if curr_o <= prev_c and curr_c >= prev_o and curr_body > prev_body:
                results.append(PatternResult("Bullish Engulfing", i, 0.9, "Bull candle completely engulfs previous bear body"))

        # Bearish Engulfing
        if prev_c > prev_o and curr_c < curr_o:
            if curr_o >= prev_c and curr_c <= prev_o and curr_body > prev_body:
                results.append(PatternResult("Bearish Engulfing", i, 0.9, "Bear candle completely engulfs previous bull body"))

    return results

def detect_double_top_bottom(highs: list[float], lows: list[float], window: int = 5, tolerance_pct: float = 2.0) -> list[PatternResult]:
    results: list[PatternResult] = []
    n = len(highs)
    if n < window * 2 + 1:
        return results

    supports = []
    resistances = []

    for i in range(window, n - window):
        is_res = True
        is_sup = True
        for j in range(1, window + 1):
            if highs[i] <= highs[i - j] or highs[i] < highs[i + j]:
                is_res = False
            if lows[i] >= lows[i - j] or lows[i] > lows[i + j]:
                is_sup = False

        if is_res:
            resistances.append((i, highs[i]))
        if is_sup:
            supports.append((i, lows[i]))

    # Check Double Tops
    for i in range(len(resistances) - 1):
        idx1, p1 = resistances[i]
        idx2, p2 = resistances[i+1]

        diff = abs(p1 - p2) / max(p1, p2) * 100
        if diff <= tolerance_pct:
            intermediate_supports = [s for s in supports if idx1 < s[0] < idx2]
            if intermediate_supports:
                neckline_idx, neckline_price = min(intermediate_supports, key=lambda x: x[1])

                for k in range(idx2 + 1, n):
                    if lows[k] < neckline_price:
                        results.append(PatternResult(
                            pattern_name="Double Top",
                            index=k,
                            confidence=0.85,
                            evidence=f"Tops at {p1:.2f} and {p2:.2f}, broke neckline at {neckline_price:.2f}"
                        ))
                        break

    # Check Double Bottoms
    for i in range(len(supports) - 1):
        idx1, p1 = supports[i]
        idx2, p2 = supports[i+1]

        diff = abs(p1 - p2) / max(p1, p2) * 100
        if diff <= tolerance_pct:
            intermediate_res = [r for r in resistances if idx1 < r[0] < idx2]
            if intermediate_res:
                neckline_idx, neckline_price = max(intermediate_res, key=lambda x: x[1])

                for k in range(idx2 + 1, n):
                    if highs[k] > neckline_price:
                        results.append(PatternResult(
                            pattern_name="Double Bottom",
                            index=k,
                            confidence=0.85,
                            evidence=f"Bottoms at {p1:.2f} and {p2:.2f}, broke neckline at {neckline_price:.2f}"
                        ))
                        break

    return results

def detect_patterns(opens: list[float], highs: list[float], lows: list[float], closes: list[float]) -> list[PatternResult]:
    results: list[PatternResult] = []
    if not opens:
        return results

    results.extend(detect_doji(opens, highs, lows, closes))
    results.extend(detect_engulfing(opens, highs, lows, closes))
    results.extend(detect_double_top_bottom(highs, lows))

    results.sort(key=lambda x: x.index)
    return results

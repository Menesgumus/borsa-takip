from app.technical.patterns import detect_doji, detect_double_top_bottom, detect_engulfing
from app.technical.support_resistance import calculate_support_resistance, find_pivots


def test_support_resistance_golden():
    # Construct an array with clear peaks at 110 and troughs at 90
    highs = [100, 105, 110, 108, 105, 100, 95, 90, 95, 100, 105, 110.5, 108, 105]
    lows  = [95, 100, 105, 103, 100, 95, 90, 85, 90, 95, 100, 105.5, 103, 100]

    # window = 2
    supports, resistances = find_pivots(highs, lows, window=2)
    # peak 1 at index 2: high=110, peak 2 at index 11: high=110.5
    assert 110 in resistances
    assert 110.5 in resistances

    # trough 1 at index 7: low=85
    assert 85 in supports

    # Check clustering
    levels = calculate_support_resistance(highs, lows, window=2, cluster_threshold_pct=1.0)

    # 110 and 110.5 should be clustered into one resistance (~110.25)
    res_levels = [l for l in levels if l.type == "RESISTANCE"]
    assert len(res_levels) == 1
    assert 110.0 <= res_levels[0].price <= 110.5
    assert res_levels[0].strength == 2

def test_pattern_doji():
    opens = [100.0]
    highs = [105.0]
    lows = [95.0]
    closes = [100.2]  # Body is 0.2, range is 10.0 (body/range = 0.02)

    res = detect_doji(opens, highs, lows, closes)
    assert len(res) == 1
    assert res[0].pattern_name == "Doji"

def test_pattern_engulfing():
    opens = [100.0, 95.0]
    highs = [102.0, 106.0]
    lows =  [94.0,  93.0]
    closes= [96.0,  105.0]
    # Prev: red candle, body 4 (100-96)
    # Curr: green candle, body 10 (95-105). Open 95 <= prev_c 96. Close 105 >= prev_o 100

    res = detect_engulfing(opens, highs, lows, closes)
    assert len(res) == 1
    assert res[0].pattern_name == "Bullish Engulfing"
    assert res[0].index == 1

def test_pattern_double_top():
    # Window=1 for simplicity
    # indices: 0   1   2   3   4   5   6
    highs = [100, 110, 105, 110.5, 105, 100, 90]
    lows =  [90,  100, 95,  100.5, 95,  90, 80]
    # Peak 1 at idx 1 (high 110)
    # Valley at idx 2 (low 95) - Neckline
    # Peak 2 at idx 3 (high 110.5)
    # Break neckline (95) at idx 6 (low 80)

    res = detect_double_top_bottom(highs, lows, window=1, tolerance_pct=2.0)
    assert len(res) == 1
    assert res[0].pattern_name == "Double Top"
    assert res[0].index == 5
    assert "110" in res[0].evidence

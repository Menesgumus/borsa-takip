import math

from app.technical.indicators import calculate_ema, calculate_macd, calculate_rsi, calculate_sma


def test_sma_golden():
    data = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]
    expected = [None, None, 11.0, 12.0, 13.0, 14.0, 15.0]
    result = calculate_sma(data, 3)
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        if e is None:
            assert r is None
        else:
            assert math.isclose(r, e, rel_tol=1e-5)

def test_ema_golden():
    data = [10.0, 11.0, 12.0, 13.0, 14.0]
    expected = [None, None, 11.0, 12.0, 13.0]
    result = calculate_ema(data, 3)
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        if e is None:
            assert r is None
        else:
            assert math.isclose(r, e, rel_tol=1e-5)

def test_rsi_golden():
    data = [
        44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
        45.84, 46.08, 45.89, 45.22, 45.36, 45.46, 45.01, 45.30
    ]
    result = calculate_rsi(data, 14)
    assert result[14] is not None
    assert math.isclose(result[14], 56.88, abs_tol=0.1)
    assert result[15] is not None
    assert math.isclose(result[15], 59.47, abs_tol=0.1)

def test_macd_golden():
    data = [
        22.27, 22.19, 22.08, 22.17, 22.18, 22.13, 22.23, 22.43, 22.24, 22.29,
        22.15, 22.39, 22.38, 22.61, 23.36, 24.05, 23.75, 23.83, 23.95, 23.63,
        23.82, 23.87, 23.65, 23.19, 23.10, 23.33, 22.68, 23.10, 22.40, 22.17,
        22.10, 22.05, 21.90, 21.80, 21.50, 21.40, 21.10, 21.00, 20.80, 20.70
    ]
    result = calculate_macd(data, 12, 26, 9)
    assert len(result) == len(data)

    last = result[-1]
    assert last.macd_line is not None
    assert last.signal_line is not None
    assert last.histogram is not None

    assert result[24].macd_line is None
    assert result[25].macd_line is not None

def test_insufficient_history():
    data = [1.0, 2.0]
    sma = calculate_sma(data, 5)
    assert sma == [None, None]

    ema = calculate_ema(data, 5)
    assert ema == [None, None]

    rsi = calculate_rsi(data, 5)
    assert rsi == [None, None]

    macd = calculate_macd(data, 12, 26, 9)
    assert macd[0].macd_line is None


def calculate_sma(data: list[float], period: int) -> list[float | None]:
    """
    Calculate Simple Moving Average.
    Returns a list of the same length as data.
    Values before period are None.
    """
    if period <= 0:
        raise ValueError("Period must be > 0")

    result: list[float | None] = []

    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            window = data[i - period + 1 : i + 1]
            result.append(sum(window) / period)

    return result

def calculate_ema(data: list[float], period: int) -> list[float | None]:
    """
    Calculate Exponential Moving Average.
    Uses SMA for the first valid period as the seed.
    """
    if period <= 0:
        raise ValueError("Period must be > 0")

    result: list[float | None] = []
    multiplier = 2 / (period + 1)

    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        elif i == period - 1:
            # Seed with SMA
            window = data[0 : period]
            result.append(sum(window) / period)
        else:
            prev_ema = result[-1]
            if prev_ema is None:
                continue # Should not happen
            current_ema = (data[i] - prev_ema) * multiplier + prev_ema
            result.append(current_ema)

    return result

def calculate_rsi(data: list[float], period: int = 14) -> list[float | None]:
    """
    Calculate Relative Strength Index using Wilder's Smoothing.
    """
    if period <= 0:
        raise ValueError("Period must be > 0")

    result: list[float | None] = []

    if len(data) <= period:
        return [None] * len(data)

    avg_gain = 0.0
    avg_loss = 0.0

    # First calculate simple average of gains and losses for the seed
    for i in range(1, period + 1):
        diff = data[i] - data[i - 1]
        if diff >= 0:
            avg_gain += diff
        else:
            avg_loss += abs(diff)

    avg_gain /= period
    avg_loss /= period

    for i in range(len(data)):
        if i <= period:
            if i < period:
                result.append(None)
            else:
                if avg_loss == 0:
                    rs = float('inf')
                    rsi = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100.0 - (100.0 / (1.0 + rs))
                result.append(rsi)
        else:
            diff = data[i] - data[i - 1]
            gain = diff if diff >= 0 else 0.0
            loss = abs(diff) if diff < 0 else 0.0

            # Wilder's smoothing
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100.0 - (100.0 / (1.0 + rs))
            result.append(rsi)

    return result

class MACDResult:
    def __init__(self, macd_line: float | None, signal_line: float | None, histogram: float | None):
        self.macd_line = macd_line
        self.signal_line = signal_line
        self.histogram = histogram

def calculate_macd(data: list[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> list[MACDResult]:
    """
    Calculate MACD (fast_period, slow_period, signal_period).
    Returns list of MACDResult objects.
    """
    fast_ema = calculate_ema(data, fast_period)
    slow_ema = calculate_ema(data, slow_period)

    macd_line: list[float | None] = []
    for i in range(len(data)):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            macd_line.append(fast_ema[i] - slow_ema[i]) # type: ignore
        else:
            macd_line.append(None)

    # Extract only the non-None MACD values to calculate the signal line (EMA of MACD)
    valid_macd_indices = [i for i, v in enumerate(macd_line) if v is not None]

    if not valid_macd_indices:
        return [MACDResult(None, None, None)] * len(data)

    first_valid_idx = valid_macd_indices[0]
    valid_macd_values = [v for v in macd_line if v is not None]

    # Calculate EMA on valid MACD values
    signal_line_valid = calculate_ema(valid_macd_values, signal_period) # type: ignore

    result: list[MACDResult] = []

    for i in range(len(data)):
        m_val = macd_line[i]

        if i < first_valid_idx:
            result.append(MACDResult(None, None, None))
        else:
            s_val = signal_line_valid[i - first_valid_idx]
            h_val = (m_val - s_val) if m_val is not None and s_val is not None else None
            result.append(MACDResult(m_val, s_val, h_val))

    return result

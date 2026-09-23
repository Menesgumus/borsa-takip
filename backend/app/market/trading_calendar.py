from datetime import date, timedelta
from typing import List

# Fixed public holidays in Turkey (month, day)
TR_FIXED_HOLIDAYS = {
    (1, 1),   # New Year's Day
    (4, 23),  # National Sovereignty and Children's Day
    (5, 1),   # Labor and Solidarity Day
    (5, 19),  # Commemoration of Ataturk, Youth and Sports Day
    (7, 15),  # Democracy and National Unity Day
    (8, 30),  # Victory Day
    (10, 29), # Republic Day
}

def is_weekend(dt: date) -> bool:
    """Returns True if the given date is a weekend (Saturday or Sunday)."""
    return dt.weekday() >= 5

def is_fixed_holiday(dt: date) -> bool:
    """Returns True if the given date is a fixed public holiday in Turkey."""
    return (dt.month, dt.day) in TR_FIXED_HOLIDAYS

def is_trading_day(dt: date, calendar_name: str = "BIST") -> bool:
    """
    Check if a specific date is a trading day.
    For now, supports fixed holidays and weekends for BIST.
    Note: Moving holidays (Eid al-Fitr, Eid al-Adha) are complex and not fully covered here without a dynamic calendar source.
    """
    if is_weekend(dt):
        return False
    if is_fixed_holiday(dt):
        return False
    return True

def get_trading_days(start_date: date, end_date: date, calendar_name: str = "BIST") -> List[date]:
    """Return a list of trading days between start_date and end_date (inclusive)."""
    days = []
    current = start_date
    while current <= end_date:
        if is_trading_day(current, calendar_name):
            days.append(current)
        current += timedelta(days=1)
    return days

def get_previous_trading_day(dt: date, calendar_name: str = "BIST") -> date:
    """Return the closest trading day strictly before the given date."""
    current = dt - timedelta(days=1)
    while not is_trading_day(current, calendar_name):
        current -= timedelta(days=1)
    return current

def get_next_trading_day(dt: date, calendar_name: str = "BIST") -> date:
    """Return the closest trading day strictly after the given date."""
    current = dt + timedelta(days=1)
    while not is_trading_day(current, calendar_name):
        current += timedelta(days=1)
    return current

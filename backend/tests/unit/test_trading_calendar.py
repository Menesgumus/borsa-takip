from datetime import date
from app.market.trading_calendar import (
    is_weekend,
    is_trading_day,
    get_session_type,
    get_trading_days,
    get_previous_trading_day,
    get_next_trading_day,
)

def test_is_weekend():
    # Saturday
    assert is_weekend(date(2023, 1, 7)) == True
    # Sunday
    assert is_weekend(date(2023, 1, 8)) == True
    # Monday
    assert is_weekend(date(2023, 1, 9)) == False

def test_get_session_type():
    # Regular day
    assert get_session_type(date(2023, 1, 2)) == "REGULAR"
    # Weekend
    assert get_session_type(date(2023, 1, 7)) == "CLOSED_WEEKEND"
    # Fixed Holiday (May 1)
    assert get_session_type(date(2023, 5, 1)) == "CLOSED_HOLIDAY"
    # Fixed Half Day (Oct 28, 2024 is a Monday)
    assert get_session_type(date(2024, 10, 28)) == "HALF_DAY"
    # Ramazan Bayramı (Variable)
    assert get_session_type(date(2023, 4, 21)) == "CLOSED_HOLIDAY"
    # Ramazan Arife (Variable Half Day)
    assert get_session_type(date(2023, 4, 20)) == "HALF_DAY"

def test_is_trading_day():
    # Regular day (Monday, not holiday)
    assert is_trading_day(date(2023, 1, 2)) == True
    # Weekend
    assert is_trading_day(date(2023, 1, 7)) == False
    # Holiday (May 1, Monday)
    assert is_trading_day(date(2023, 5, 1)) == False
    # Arife (Half day is a trading day)
    assert is_trading_day(date(2023, 4, 20)) == True
    # Ramazan (Holiday is closed)
    assert is_trading_day(date(2023, 4, 21)) == False

def test_get_trading_days():
    # Dec 31 (Sat), Jan 1 (Sun, Holiday), Jan 2 (Mon, Trading), Jan 3 (Tue, Trading)
    days = get_trading_days(date(2022, 12, 31), date(2023, 1, 3))
    assert days == [date(2023, 1, 2), date(2023, 1, 3)]

def test_get_previous_trading_day():
    # Jan 2 (Mon) -> prev should be Dec 30 (Fri)
    assert get_previous_trading_day(date(2023, 1, 2)) == date(2022, 12, 30)
    # May 2 (Tue) -> prev should be Apr 28 (Fri) because May 1 is a holiday, and Apr 29/30 is weekend
    assert get_previous_trading_day(date(2023, 5, 2)) == date(2023, 4, 28)

def test_get_next_trading_day():
    # Dec 30 (Fri) -> next should be Jan 2 (Mon)
    assert get_next_trading_day(date(2022, 12, 30)) == date(2023, 1, 2)
    # Apr 28 (Fri) -> next should be May 2 (Tue)
    assert get_next_trading_day(date(2023, 4, 28)) == date(2023, 5, 2)

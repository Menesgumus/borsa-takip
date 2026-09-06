import time

from app.core.security import get_password_hash, verify_password


def test_password_hashing():
    password = "SuperSecretPassword123!"

    # Measure hashing time
    start_time = time.perf_counter()
    hashed = get_password_hash(password)
    end_time = time.perf_counter()

    duration_ms = (end_time - start_time) * 1000
    print(f"Hashing duration: {duration_ms:.2f} ms")

    assert duration_ms < 300, f"Hashing is too slow: {duration_ms} ms (expected < 300ms)"

    # Test valid password
    assert verify_password(password, hashed) is True

    # Test invalid password
    assert verify_password("WrongPassword", hashed) is False

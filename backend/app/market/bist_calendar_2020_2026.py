"""
Authoritative versioned BIST calendar dataset for 2020-2026.
Contains explicitly defined Ramazan Bayramı, Kurban Bayramı, and arife (half-day) closures.
"""
from datetime import date

# Format: date: "SESSION_TYPE"
# Types: CLOSED_HOLIDAY, HALF_DAY, EXCEPTIONAL_CLOSURE
BIST_VARIABLE_HOLIDAYS = {
    # 2020
    date(2020, 5, 23): "HALF_DAY", # Ramazan Arife
    date(2020, 5, 24): "CLOSED_HOLIDAY", # Ramazan 1
    date(2020, 5, 25): "CLOSED_HOLIDAY", # Ramazan 2
    date(2020, 5, 26): "CLOSED_HOLIDAY", # Ramazan 3
    date(2020, 7, 30): "HALF_DAY", # Kurban Arife
    date(2020, 7, 31): "CLOSED_HOLIDAY", # Kurban 1
    date(2020, 8, 1): "CLOSED_HOLIDAY", # Kurban 2
    date(2020, 8, 2): "CLOSED_HOLIDAY", # Kurban 3
    date(2020, 8, 3): "CLOSED_HOLIDAY", # Kurban 4

    # 2021
    date(2021, 5, 12): "HALF_DAY", # Ramazan Arife
    date(2021, 5, 13): "CLOSED_HOLIDAY", # Ramazan 1
    date(2021, 5, 14): "CLOSED_HOLIDAY", # Ramazan 2
    date(2021, 5, 15): "CLOSED_HOLIDAY", # Ramazan 3
    date(2021, 7, 19): "HALF_DAY", # Kurban Arife
    date(2021, 7, 20): "CLOSED_HOLIDAY", # Kurban 1
    date(2021, 7, 21): "CLOSED_HOLIDAY", # Kurban 2
    date(2021, 7, 22): "CLOSED_HOLIDAY", # Kurban 3
    date(2021, 7, 23): "CLOSED_HOLIDAY", # Kurban 4

    # 2022
    date(2022, 5, 1): "HALF_DAY", # Ramazan Arife
    date(2022, 5, 2): "CLOSED_HOLIDAY", # Ramazan 1
    date(2022, 5, 3): "CLOSED_HOLIDAY", # Ramazan 2
    date(2022, 5, 4): "CLOSED_HOLIDAY", # Ramazan 3
    date(2022, 7, 8): "HALF_DAY", # Kurban Arife
    date(2022, 7, 9): "CLOSED_HOLIDAY", # Kurban 1
    date(2022, 7, 10): "CLOSED_HOLIDAY", # Kurban 2
    date(2022, 7, 11): "CLOSED_HOLIDAY", # Kurban 3
    date(2022, 7, 12): "CLOSED_HOLIDAY", # Kurban 4

    # 2023
    date(2023, 2, 8): "EXCEPTIONAL_CLOSURE", # Earthquake
    date(2023, 2, 9): "EXCEPTIONAL_CLOSURE", # Earthquake
    date(2023, 2, 10): "EXCEPTIONAL_CLOSURE", # Earthquake
    date(2023, 2, 13): "EXCEPTIONAL_CLOSURE", # Earthquake
    date(2023, 2, 14): "EXCEPTIONAL_CLOSURE", # Earthquake
    date(2023, 4, 20): "HALF_DAY", # Ramazan Arife
    date(2023, 4, 21): "CLOSED_HOLIDAY", # Ramazan 1
    date(2023, 4, 22): "CLOSED_HOLIDAY", # Ramazan 2
    date(2023, 4, 23): "CLOSED_HOLIDAY", # Ramazan 3
    date(2023, 6, 27): "HALF_DAY", # Kurban Arife
    date(2023, 6, 28): "CLOSED_HOLIDAY", # Kurban 1
    date(2023, 6, 29): "CLOSED_HOLIDAY", # Kurban 2
    date(2023, 6, 30): "CLOSED_HOLIDAY", # Kurban 3
    date(2023, 7, 1): "CLOSED_HOLIDAY", # Kurban 4

    # 2024
    date(2024, 4, 9): "HALF_DAY", # Ramazan Arife
    date(2024, 4, 10): "CLOSED_HOLIDAY", # Ramazan 1
    date(2024, 4, 11): "CLOSED_HOLIDAY", # Ramazan 2
    date(2024, 4, 12): "CLOSED_HOLIDAY", # Ramazan 3
    date(2024, 6, 15): "HALF_DAY", # Kurban Arife
    date(2024, 6, 16): "CLOSED_HOLIDAY", # Kurban 1
    date(2024, 6, 17): "CLOSED_HOLIDAY", # Kurban 2
    date(2024, 6, 18): "CLOSED_HOLIDAY", # Kurban 3
    date(2024, 6, 19): "CLOSED_HOLIDAY", # Kurban 4

    # 2025
    date(2025, 3, 29): "HALF_DAY", # Ramazan Arife
    date(2025, 3, 30): "CLOSED_HOLIDAY", # Ramazan 1
    date(2025, 3, 31): "CLOSED_HOLIDAY", # Ramazan 2
    date(2025, 4, 1): "CLOSED_HOLIDAY", # Ramazan 3
    date(2025, 6, 5): "HALF_DAY", # Kurban Arife
    date(2025, 6, 6): "CLOSED_HOLIDAY", # Kurban 1
    date(2025, 6, 7): "CLOSED_HOLIDAY", # Kurban 2
    date(2025, 6, 8): "CLOSED_HOLIDAY", # Kurban 3
    date(2025, 6, 9): "CLOSED_HOLIDAY", # Kurban 4

    # 2026
    date(2026, 3, 19): "HALF_DAY", # Ramazan Arife
    date(2026, 3, 20): "CLOSED_HOLIDAY", # Ramazan 1
    date(2026, 3, 21): "CLOSED_HOLIDAY", # Ramazan 2
    date(2026, 3, 22): "CLOSED_HOLIDAY", # Ramazan 3
    date(2026, 5, 26): "HALF_DAY", # Kurban Arife
    date(2026, 5, 27): "CLOSED_HOLIDAY", # Kurban 1
    date(2026, 5, 28): "CLOSED_HOLIDAY", # Kurban 2
    date(2026, 5, 29): "CLOSED_HOLIDAY", # Kurban 3
    date(2026, 5, 30): "CLOSED_HOLIDAY", # Kurban 4
}

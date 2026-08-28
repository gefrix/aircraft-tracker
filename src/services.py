from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from src.aeroplane import Aeroplane

ALTITUDE_RANGE_PATTERN = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*[-–—:]\s*(-?\d+(?:[.,]\d+)?)\s*$")


def filter_aeroplanes(aeroplanes: Iterable[Aeroplane], countries: Iterable[str]) -> list[Aeroplane]:
    """Filter aircraft by registration countries, ignoring letter case."""
    normalized = {country.strip().casefold() for country in countries if country.strip()}
    items = list(aeroplanes)
    if not normalized:
        return items
    return [item for item in items if item.origin_country.casefold() in normalized]


def parse_altitude_range(value: str) -> tuple[float, float]:
    """Parse an altitude range such as ``1000 - 15000``."""
    match = ALTITUDE_RANGE_PATTERN.fullmatch(value)
    if not match:
        raise ValueError("Диапазон высот должен быть указан в формате 1000 - 15000")
    lower = float(match.group(1).replace(",", "."))
    upper = float(match.group(2).replace(",", "."))
    if lower > upper:
        raise ValueError("Нижняя граница высоты не может быть больше верхней")
    return lower, upper


def get_aeroplanes_by_altitude(
    aeroplanes: Iterable[Aeroplane],
    altitude_range: str | tuple[float, float],
) -> list[Aeroplane]:
    """Return aircraft whose altitude is inside the inclusive range."""
    lower, upper = parse_altitude_range(altitude_range) if isinstance(altitude_range, str) else altitude_range
    if lower > upper:
        raise ValueError("Нижняя граница высоты не может быть больше верхней")
    return [item for item in aeroplanes if lower <= item.altitude <= upper]


def sort_aeroplanes(aeroplanes: Iterable[Aeroplane]) -> list[Aeroplane]:
    """Sort aircraft by altitude and velocity in descending order."""
    return sorted(aeroplanes, key=lambda item: (item.altitude, item.velocity), reverse=True)


def get_top_aeroplanes(aeroplanes: Sequence[Aeroplane], top_n: int) -> list[Aeroplane]:
    """Return at most N aircraft from an already ordered sequence."""
    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("Количество самолетов в топе должно быть положительным целым числом")
    return list(aeroplanes[:top_n])


def print_aeroplanes(aeroplanes: Iterable[Aeroplane]) -> str:
    """Build a numbered human-readable aircraft list."""
    items = list(aeroplanes)
    if not items:
        return "Самолеты по заданным критериям не найдены."
    return "\n".join(f"{number}. {item}" for number, item in enumerate(items, start=1))

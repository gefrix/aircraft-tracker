from __future__ import annotations

import pytest

from src.aeroplane import Aeroplane
from src.services import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    parse_altitude_range,
    print_aeroplanes,
    sort_aeroplanes,
)


def test_filter_by_registration_country_is_case_insensitive(aeroplanes: list[Aeroplane]) -> None:
    result = filter_aeroplanes(aeroplanes, ["france"])

    assert [item.callsign for item in result] == ["LOW100", "MID300"]
    assert filter_aeroplanes(aeroplanes, []) == aeroplanes


def test_parse_altitude_range_supports_common_formats() -> None:
    assert parse_altitude_range("1000 - 15000") == (1000.0, 15000.0)
    assert parse_altitude_range("1000,5:15000,5") == (1000.5, 15000.5)


@pytest.mark.parametrize("value", ["", "1000", "high - low", "2000 - 1000"])
def test_invalid_altitude_range_is_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        parse_altitude_range(value)


def test_filter_by_altitude_is_inclusive(aeroplanes: list[Aeroplane]) -> None:
    result = get_aeroplanes_by_altitude(aeroplanes, "2000 - 7000")

    assert [item.callsign for item in result] == ["LOW100", "MID300"]
    with pytest.raises(ValueError, match="Нижняя"):
        get_aeroplanes_by_altitude(aeroplanes, (9000, 1000))


def test_sort_and_top_are_descending(aeroplanes: list[Aeroplane]) -> None:
    sorted_items = sort_aeroplanes(aeroplanes)

    assert [item.callsign for item in sorted_items] == ["HIGH200", "MID300", "LOW100"]
    assert get_top_aeroplanes(sorted_items, 2) == sorted_items[:2]


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_top_rejects_invalid_n(value: object, aeroplanes: list[Aeroplane]) -> None:
    with pytest.raises(ValueError, match="положительным"):
        get_top_aeroplanes(aeroplanes, value)  # type: ignore[arg-type]


def test_human_readable_output(aeroplanes: list[Aeroplane]) -> None:
    output = print_aeroplanes(aeroplanes[:1])

    assert output.startswith("1. LOW100 — France")
    assert "высота: 2000 м" in output
    assert print_aeroplanes([]) == "Самолеты по заданным критериям не найдены."

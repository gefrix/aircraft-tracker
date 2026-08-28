from __future__ import annotations

import math
from collections.abc import Sequence

import pytest

from src.aeroplane import Aeroplane
from src.exceptions import AeroplaneValidationError


def test_initialization_uses_private_typed_attributes() -> None:
    aeroplane = Aeroplane(
        " UAL1621 ",
        " United States ",
        268.79,
        10203.18,
        "ABC123",
        False,
        -0.02,
        51.09,
    )

    assert aeroplane.callsign == "UAL1621"
    assert aeroplane.origin_country == "United States"
    assert aeroplane.velocity == 268.79
    assert aeroplane.altitude == 10203.18
    assert aeroplane.icao24 == "abc123"
    assert aeroplane.longitude == -0.02
    assert aeroplane.latitude == 51.09
    assert not hasattr(aeroplane, "__velocity")
    assert aeroplane._Aeroplane__velocity == 268.79


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (("", "France", 10, 100), "Позывной"),
        (("ABC", " ", 10, 100), "Страна регистрации"),
        (("ABC", "France", -1, 100), "Скорость"),
        (("ABC", "France", math.inf, 100), "Скорость"),
        (("ABC", "France", 10, math.nan), "Высота"),
    ],
)
def test_invalid_required_data_is_rejected(arguments: tuple[object, ...], message: str) -> None:
    with pytest.raises(AeroplaneValidationError, match=message):
        Aeroplane(*arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("keyword", "value", "message"),
    [
        ("longitude", 181.0, "Долгота"),
        ("latitude", -91.0, "Широта"),
        ("on_ground", "no", "логическим"),
        ("icao24", 123, "ICAO24"),
    ],
)
def test_invalid_optional_data_is_rejected(keyword: str, value: object, message: str) -> None:
    kwargs = {keyword: value}
    with pytest.raises(AeroplaneValidationError, match=message):
        Aeroplane("ABC", "France", 10, 100, **kwargs)  # type: ignore[arg-type]


def test_from_state_vector_maps_opensky_fields(state_vector: list[object]) -> None:
    aeroplane = Aeroplane.from_state_vector(state_vector)

    assert aeroplane.callsign == "SWR438A"
    assert aeroplane.origin_country == "Switzerland"
    assert aeroplane.velocity == 189.7
    assert aeroplane.altitude == 4267.2
    assert aeroplane.icao24 == "4b1812"
    assert aeroplane.longitude == -0.0168
    assert aeroplane.latitude == 51.0888


def test_from_state_vector_uses_safe_fallbacks(state_vector: list[object]) -> None:
    state_vector[1] = None
    state_vector[2] = None
    state_vector[7] = None
    state_vector[9] = None

    aeroplane = Aeroplane.from_state_vector(state_vector)

    assert aeroplane.callsign == "Без позывного"
    assert aeroplane.origin_country == "Неизвестно"
    assert aeroplane.velocity == 0.0
    assert aeroplane.altitude == 4282.44


def test_short_state_vector_is_rejected() -> None:
    with pytest.raises(AeroplaneValidationError, match="17 полей"):
        Aeroplane.from_state_vector(["too", "short"])


def test_cast_to_object_list_skips_invalid_rows(state_vectors: list[Sequence[object]]) -> None:
    data: list[object] = [*state_vectors, "invalid", ["short"]]

    result = Aeroplane.cast_to_object_list({"states": data})

    assert [item.callsign for item in result] == ["SWR438A", "UAL1621"]
    assert Aeroplane.cast_to_object_list({"states": None}) == []


def test_cast_to_object_list_rejects_invalid_root() -> None:
    with pytest.raises(AeroplaneValidationError, match="неверный формат"):
        Aeroplane.cast_to_object_list("invalid")


def test_speed_and_altitude_comparisons() -> None:
    first = Aeroplane("FIRST", "France", 250.0, 5000.0)
    second = Aeroplane("SECOND", "Spain", 200.0, 8000.0)

    assert first.compare_speed(second) == 1
    assert second.compare_speed(first) == -1
    assert first.compare_speed(first) == 0
    assert first.is_faster_than(second)
    assert second.compare_altitude(first) == 1
    assert second.is_higher_than(first)
    assert first < second


def test_comparison_rejects_other_types() -> None:
    aeroplane = Aeroplane("FIRST", "France", 250.0, 5000.0)

    with pytest.raises(TypeError, match="только самолеты"):
        aeroplane.compare_speed("not an aircraft")  # type: ignore[arg-type]


def test_json_round_trip_and_string_representation() -> None:
    source = Aeroplane("UAL1621", "United States", 268.79, 10203.18, "abc123")

    restored = Aeroplane.from_dict(source.to_dict())

    assert restored.to_dict() == source.to_dict()
    assert str(restored) == ("UAL1621 — United States; высота: 10203 м; скорость: 268.8 м/с; в полете")

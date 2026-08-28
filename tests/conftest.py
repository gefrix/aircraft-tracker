from __future__ import annotations

from collections.abc import Sequence

import pytest

from src.aeroplane import Aeroplane


@pytest.fixture
def state_vector() -> list[object]:
    return [
        "4b1812",
        "SWR438A ",
        "Switzerland",
        1766166618,
        1766166618,
        -0.0168,
        51.0888,
        4267.2,
        False,
        189.7,
        129.39,
        14.63,
        None,
        4282.44,
        "2061",
        False,
        0,
    ]


@pytest.fixture
def state_vectors(state_vector: list[object]) -> list[Sequence[object]]:
    second = list(state_vector)
    second[0] = "abc123"
    second[1] = "UAL1621"
    second[2] = "United States"
    second[7] = 10203.18
    second[9] = 268.79
    return [state_vector, second]


@pytest.fixture
def aeroplanes() -> list[Aeroplane]:
    return [
        Aeroplane("LOW100", "France", 150.0, 2000.0, "aaa111"),
        Aeroplane("HIGH200", "United States", 240.0, 11000.0, "bbb222"),
        Aeroplane("MID300", "France", 200.0, 7000.0, "ccc333"),
    ]

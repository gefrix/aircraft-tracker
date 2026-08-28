from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from src.api import AeroplanesAPI, APIAdapter
from src.base_api import BaseAPI
from src.exceptions import APIError, CountryNotFoundError


def _response(payload: object) -> Mock:
    response = Mock()
    response.json.return_value = payload
    return response


def test_api_inherits_abstract_interface() -> None:
    assert issubclass(AeroplanesAPI, BaseAPI)
    assert APIAdapter is AeroplanesAPI


def test_get_country_bounds_returns_float_tuple() -> None:
    session = Mock(spec=requests.Session)
    session.get.return_value = _response([{"boundingbox": ["36.0", "43.8", "-9.5", "3.4"]}])
    api = AeroplanesAPI(session=session)

    result = api.get_country_bounds("Spain")

    assert result == (36.0, 43.8, -9.5, 3.4)
    session.get.assert_called_once_with(
        AeroplanesAPI.NOMINATIM_URL,
        params={"country": "Spain", "format": "jsonv2", "limit": 1},
        headers={"User-Agent": "aircraft-tracker-coursework/1.0"},
        timeout=15.0,
    )


def test_get_aeroplanes_uses_country_bounds(state_vector: list[object]) -> None:
    session = Mock(spec=requests.Session)
    session.get.side_effect = [
        _response([{"boundingbox": ["36", "44", "-10", "4"]}]),
        _response({"time": 1, "states": [state_vector]}),
    ]
    api = AeroplanesAPI(session=session)

    result = api.get_aeroplanes("Spain")

    assert result == [state_vector]
    assert api.aeroplanes == result
    assert session.get.call_args_list[1].kwargs["params"] == {
        "lamin": 36.0,
        "lamax": 44.0,
        "lomin": -10.0,
        "lomax": 4.0,
    }


def test_get_aeroplanes_converts_null_states_to_empty_list() -> None:
    session = Mock(spec=requests.Session)
    session.get.side_effect = [
        _response([{"boundingbox": ["36", "44", "-10", "4"]}]),
        _response({"time": 1, "states": None}),
    ]

    assert AeroplanesAPI(session=session).get_aeroplanes("Spain") == []


def test_country_not_found_is_reported() -> None:
    session = Mock(spec=requests.Session)
    session.get.return_value = _response([])

    with pytest.raises(CountryNotFoundError, match="не найдена"):
        AeroplanesAPI(session=session).get_country_bounds("Nowhere")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        ["invalid"],
        [{"boundingbox": ["1", "2"]}],
        [{"boundingbox": ["south", "2", "3", "4"]}],
    ],
)
def test_invalid_nominatim_payload_is_reported(payload: object) -> None:
    session = Mock(spec=requests.Session)
    session.get.return_value = _response(payload)

    with pytest.raises(APIError):
        AeroplanesAPI(session=session).get_country_bounds("Spain")


def test_network_error_is_wrapped() -> None:
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.Timeout("slow")

    with pytest.raises(APIError, match="координаты"):
        AeroplanesAPI(session=session).get_country_bounds("Spain")


def test_invalid_opensky_payload_is_reported() -> None:
    session = Mock(spec=requests.Session)
    session.get.side_effect = [
        _response([{"boundingbox": ["36", "44", "-10", "4"]}]),
        _response({"states": "invalid"}),
    ]

    with pytest.raises(APIError, match="states"):
        AeroplanesAPI(session=session).get_aeroplanes("Spain")


def test_blank_country_and_invalid_timeout_are_rejected() -> None:
    with pytest.raises(ValueError, match="страны"):
        AeroplanesAPI().get_country_bounds(" ")
    with pytest.raises(ValueError, match="Тайм-аут"):
        AeroplanesAPI(timeout=0)

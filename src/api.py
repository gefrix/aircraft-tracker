from __future__ import annotations

from typing import cast

import requests

from src.aeroplane import StateVector
from src.base_api import BaseAPI, CountryBounds
from src.exceptions import APIError, CountryNotFoundError


class AeroplanesAPI(BaseAPI):
    """Load country boundaries from Nominatim and aircraft from OpenSky."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = 15.0,
        user_agent: str = "aircraft-tracker-coursework/1.0",
    ) -> None:
        if timeout <= 0:
            raise ValueError("Тайм-аут должен быть положительным")
        self._session = session or requests.Session()
        self._timeout = timeout
        self._nominatim_headers = {"User-Agent": user_agent}
        self.aeroplanes: list[StateVector] = []

    def get_country_bounds(self, country: str) -> CountryBounds:
        normalized_country = country.strip()
        if not normalized_country:
            raise ValueError("Название страны не может быть пустым")

        try:
            search_params: dict[str, str | int] = {
                "country": normalized_country,
                "format": "jsonv2",
                "limit": 1,
            }
            response = self._session.get(
                self.NOMINATIM_URL,
                params=search_params,
                headers=self._nominatim_headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise APIError(f"Не удалось получить координаты страны: {error}") from error
        except ValueError as error:
            raise APIError("Nominatim вернул некорректный JSON") from error

        if not isinstance(payload, list) or not payload:
            raise CountryNotFoundError(f"Страна «{normalized_country}» не найдена")

        first_result = payload[0]
        if not isinstance(first_result, dict):
            raise APIError("Nominatim вернул координаты в неожиданном формате")
        raw_bounds = first_result.get("boundingbox")
        if not isinstance(raw_bounds, list) or len(raw_bounds) != 4:
            raise APIError("В ответе Nominatim отсутствует корректный boundingbox")

        try:
            south, north, west, east = (float(value) for value in raw_bounds)
        except (TypeError, ValueError) as error:
            raise APIError("Nominatim вернул некорректные значения boundingbox") from error
        return south, north, west, east

    def get_aeroplanes(self, country: str) -> list[StateVector]:
        south, north, west, east = self.get_country_bounds(country)
        try:
            response = self._session.get(
                self.OPENSKY_URL,
                params={"lamin": south, "lamax": north, "lomin": west, "lomax": east},
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise APIError(f"Не удалось получить данные OpenSky: {error}") from error
        except ValueError as error:
            raise APIError("OpenSky вернул некорректный JSON") from error

        if not isinstance(payload, dict):
            raise APIError("OpenSky вернул ответ в неожиданном формате")
        raw_states = payload.get("states")
        if raw_states is None:
            self.aeroplanes = []
            return []
        if not isinstance(raw_states, list):
            raise APIError("Поле states в ответе OpenSky должно быть списком")

        self.aeroplanes = cast(list[StateVector], raw_states)
        return list(self.aeroplanes)


APIAdapter = AeroplanesAPI

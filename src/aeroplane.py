from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, TypeAlias

from src.exceptions import AeroplaneValidationError

StateVector: TypeAlias = Sequence[object]


class Aeroplane:
    """Represent a validated aircraft state while keeping attributes private."""

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        altitude: float,
        icao24: str = "",
        on_ground: bool = False,
        longitude: float | None = None,
        latitude: float | None = None,
    ) -> None:
        self.__callsign = self._validate_text(callsign, "Позывной")
        self.__origin_country = self._validate_text(origin_country, "Страна регистрации")
        self.__velocity = self._validate_number(velocity, "Скорость", minimum=0.0)
        self.__altitude = self._validate_number(altitude, "Высота")
        self.__icao24 = self._validate_identifier(icao24)
        if not isinstance(on_ground, bool):
            raise AeroplaneValidationError("Признак нахождения на земле должен быть логическим значением")
        self.__on_ground = on_ground
        self.__longitude = self._validate_coordinate(longitude, "Долгота", -180.0, 180.0)
        self.__latitude = self._validate_coordinate(latitude, "Широта", -90.0, 90.0)

    @staticmethod
    def _validate_text(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise AeroplaneValidationError(f"{field} не может быть пустым")
        return value.strip()

    @staticmethod
    def _validate_identifier(value: str) -> str:
        if not isinstance(value, str):
            raise AeroplaneValidationError("ICAO24 должен быть строкой")
        return value.strip().lower()

    @staticmethod
    def _validate_number(value: object, field: str, minimum: float | None = None) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise AeroplaneValidationError(f"{field} должна быть числом")
        try:
            normalized = float(value)
        except (TypeError, ValueError) as error:
            raise AeroplaneValidationError(f"{field} должна быть числом") from error
        if not math.isfinite(normalized):
            raise AeroplaneValidationError(f"{field} должна быть конечным числом")
        if minimum is not None and normalized < minimum:
            raise AeroplaneValidationError(f"{field} не может быть меньше {minimum:g}")
        return normalized

    @classmethod
    def _validate_coordinate(
        cls,
        value: object | None,
        field: str,
        minimum: float,
        maximum: float,
    ) -> float | None:
        if value is None:
            return None
        normalized = cls._validate_number(value, field)
        if not minimum <= normalized <= maximum:
            raise AeroplaneValidationError(f"{field} должна быть в диапазоне от {minimum:g} до {maximum:g}")
        return normalized

    @property
    def callsign(self) -> str:
        return self.__callsign

    @property
    def origin_country(self) -> str:
        return self.__origin_country

    @property
    def velocity(self) -> float:
        return self.__velocity

    @property
    def altitude(self) -> float:
        return self.__altitude

    @property
    def icao24(self) -> str:
        return self.__icao24

    @property
    def on_ground(self) -> bool:
        return self.__on_ground

    @property
    def longitude(self) -> float | None:
        return self.__longitude

    @property
    def latitude(self) -> float | None:
        return self.__latitude

    @classmethod
    def from_state_vector(cls, state: StateVector) -> Aeroplane:
        """Build an object from one OpenSky state vector."""
        if isinstance(state, (str, bytes)) or len(state) < 17:
            raise AeroplaneValidationError("Вектор состояния OpenSky должен содержать не менее 17 полей")

        callsign = str(state[1]).strip() if state[1] is not None else ""
        origin_country = str(state[2]).strip() if state[2] is not None else ""
        barometric_altitude = state[7]
        geometric_altitude = state[13]
        altitude = barometric_altitude if barometric_altitude is not None else geometric_altitude

        return cls(
            callsign=callsign or "Без позывного",
            origin_country=origin_country or "Неизвестно",
            velocity=cls._validate_number(state[9] if state[9] is not None else 0.0, "Скорость", 0.0),
            altitude=cls._validate_number(altitude if altitude is not None else 0.0, "Высота"),
            icao24=str(state[0]) if state[0] is not None else "",
            on_ground=bool(state[8]),
            longitude=cls._validate_coordinate(state[5], "Долгота", -180.0, 180.0),
            latitude=cls._validate_coordinate(state[6], "Широта", -90.0, 90.0),
        )

    @classmethod
    def cast_to_object_list(cls, data: object) -> list[Aeroplane]:
        """Convert an OpenSky response or a state-vector list to valid objects."""
        raw_states: object = data.get("states", []) if isinstance(data, dict) else data
        if raw_states is None:
            return []
        if not isinstance(raw_states, list):
            raise AeroplaneValidationError("Список самолетов имеет неверный формат")

        aeroplanes: list[Aeroplane] = []
        for state in raw_states:
            if not isinstance(state, Sequence) or isinstance(state, (str, bytes)):
                continue
            try:
                aeroplanes.append(cls.from_state_vector(state))
            except (AeroplaneValidationError, TypeError, ValueError):
                continue
        return aeroplanes

    def compare_speed(self, other: Aeroplane) -> int:
        """Compare aircraft by velocity and return -1, 0 or 1."""
        self._ensure_aeroplane(other)
        return (self.velocity > other.velocity) - (self.velocity < other.velocity)

    def compare_altitude(self, other: Aeroplane) -> int:
        """Compare aircraft by altitude and return -1, 0 or 1."""
        self._ensure_aeroplane(other)
        return (self.altitude > other.altitude) - (self.altitude < other.altitude)

    def is_faster_than(self, other: Aeroplane) -> bool:
        return self.compare_speed(other) > 0

    def is_higher_than(self, other: Aeroplane) -> bool:
        return self.compare_altitude(other) > 0

    @staticmethod
    def _ensure_aeroplane(other: object) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только самолеты")

    def __lt__(self, other: Aeroplane) -> bool:
        self._ensure_aeroplane(other)
        return self.altitude < other.altitude

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "altitude": self.altitude,
            "on_ground": self.on_ground,
            "longitude": self.longitude,
            "latitude": self.latitude,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aeroplane:
        """Restore an aircraft object from JSON-compatible data."""
        return cls(
            callsign=data["callsign"],
            origin_country=data["origin_country"],
            velocity=data["velocity"],
            altitude=data["altitude"],
            icao24=data.get("icao24", ""),
            on_ground=data.get("on_ground", False),
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
        )

    def __str__(self) -> str:
        status = "на земле" if self.on_ground else "в полете"
        return (
            f"{self.callsign} — {self.origin_country}; высота: {self.altitude:.0f} м; "
            f"скорость: {self.velocity:.1f} м/с; {status}"
        )

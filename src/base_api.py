from abc import ABC, abstractmethod

from src.aeroplane import StateVector

CountryBounds = tuple[float, float, float, float]


class BaseAPI(ABC):
    """Define operations required from an aircraft data API provider."""

    @abstractmethod
    def get_country_bounds(self, country: str) -> CountryBounds:
        """Return southern, northern, western and eastern country bounds."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[StateVector]:
        """Return raw state vectors for aircraft inside a country boundary."""

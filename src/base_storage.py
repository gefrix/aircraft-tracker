from abc import ABC, abstractmethod
from collections.abc import Mapping

from src.aeroplane import Aeroplane


class BaseStorage(ABC):
    """Define storage operations independently from a concrete file format."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Add or update one aircraft record."""

    @abstractmethod
    def get_aeroplanes(self, criteria: Mapping[str, object] | None = None) -> list[Aeroplane]:
        """Return aircraft records matching optional criteria."""

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane | str) -> bool:
        """Delete one aircraft by object or ICAO24 identifier."""

"""Public package interface for the aircraft tracker."""

from src.aeroplane import Aeroplane, StateVector
from src.api import AeroplanesAPI, APIAdapter
from src.base_api import BaseAPI, CountryBounds
from src.base_storage import BaseStorage
from src.exceptions import (
    AeroplaneValidationError,
    AircraftTrackerError,
    APIError,
    CountryNotFoundError,
    StorageError,
)
from src.json_saver import JSONSaver

__all__ = [
    "APIAdapter",
    "APIError",
    "Aeroplane",
    "AeroplaneValidationError",
    "AeroplanesAPI",
    "AircraftTrackerError",
    "BaseAPI",
    "BaseStorage",
    "CountryBounds",
    "CountryNotFoundError",
    "JSONSaver",
    "StateVector",
    "StorageError",
]

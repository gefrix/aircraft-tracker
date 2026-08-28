class AircraftTrackerError(Exception):
    """Base exception for expected application errors."""


class APIError(AircraftTrackerError):
    """Report an external API request or response error."""


class CountryNotFoundError(APIError):
    """Report that Nominatim could not find a requested country."""


class AeroplaneValidationError(AircraftTrackerError, ValueError):
    """Report invalid data supplied to an aeroplane object."""


class StorageError(AircraftTrackerError):
    """Report that persistent aircraft data could not be read or written."""

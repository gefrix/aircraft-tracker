from __future__ import annotations

from collections.abc import Callable

from src.aeroplane import Aeroplane
from src.api import AeroplanesAPI
from src.base_api import BaseAPI
from src.base_storage import BaseStorage
from src.exceptions import AircraftTrackerError
from src.json_saver import JSONSaver
from src.services import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


def _read_positive_integer(input_func: InputFunction, output_func: OutputFunction) -> int:
    while True:
        raw_value = input_func("Введите количество самолетов для топа: ")
        try:
            value = int(raw_value)
            if value <= 0:
                raise ValueError
        except ValueError:
            output_func("Введите положительное целое число.")
            continue
        return value


def _split_countries(value: str) -> list[str]:
    return [country.strip() for country in value.split(",") if country.strip()]


def user_interaction(
    api: BaseAPI | None = None,
    storage: BaseStorage | None = None,
    input_func: InputFunction = input,
    output_func: OutputFunction = print,
) -> list[Aeroplane]:
    """Run the complete console workflow and return the displayed aircraft."""
    api_client = api or AeroplanesAPI()
    aircraft_storage = storage or JSONSaver()

    country = input_func("Введите название страны для поиска самолетов: ").strip()
    top_n = _read_positive_integer(input_func, output_func)
    registration_countries = _split_countries(input_func("Введите страны регистрации через запятую (Enter — все): "))
    altitude_range = input_func("Введите диапазон высот, например 1000 - 15000 (Enter — любой): ").strip()

    try:
        raw_aeroplanes = api_client.get_aeroplanes(country)
        aeroplanes = Aeroplane.cast_to_object_list(raw_aeroplanes)
        for aeroplane in aeroplanes:
            aircraft_storage.add_aeroplane(aeroplane)

        filtered = filter_aeroplanes(aeroplanes, registration_countries)
        if altitude_range:
            filtered = get_aeroplanes_by_altitude(filtered, altitude_range)
        result = get_top_aeroplanes(sort_aeroplanes(filtered), top_n)
    except (AircraftTrackerError, ValueError) as error:
        output_func(f"Не удалось выполнить запрос: {error}")
        return []

    output_func(f"Найдено самолетов в воздушном пространстве: {len(aeroplanes)}")
    output_func(print_aeroplanes(result))
    return result

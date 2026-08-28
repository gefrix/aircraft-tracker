from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.aeroplane import Aeroplane
from src.base_storage import BaseStorage
from src.exceptions import AeroplaneValidationError, StorageError


class JSONSaver(BaseStorage):
    """Persist aircraft records in a UTF-8 JSON file."""

    def __init__(self, file_path: str | Path = "data/aeroplanes.json") -> None:
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._write_data([])

    def _read_data(self) -> list[dict[str, Any]]:
        try:
            payload = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise StorageError(f"Не удалось прочитать JSON-файл: {error}") from error
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise StorageError("Корневой элемент JSON-файла должен быть списком объектов")
        return payload

    def _write_data(self, data: list[dict[str, Any]]) -> None:
        try:
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as error:
            raise StorageError(f"Не удалось записать JSON-файл: {error}") from error

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        if not isinstance(aeroplane, Aeroplane):
            raise TypeError("Сохранить можно только объект Aeroplane")

        data = self._read_data()
        identity = self._identity(aeroplane)
        for index, item in enumerate(data):
            if self._identity_from_dict(item) == identity:
                data[index] = aeroplane.to_dict()
                break
        else:
            data.append(aeroplane.to_dict())
        self._write_data(data)

    def get_aeroplanes(self, criteria: Mapping[str, object] | None = None) -> list[Aeroplane]:
        try:
            aeroplanes = [Aeroplane.from_dict(item) for item in self._read_data()]
        except (KeyError, TypeError, AeroplaneValidationError) as error:
            raise StorageError(f"JSON-файл содержит некорректную запись: {error}") from error
        if not criteria:
            return aeroplanes

        allowed_fields = set(Aeroplane("probe", "probe", 0, 0).to_dict())
        unknown_fields = set(criteria) - allowed_fields
        if unknown_fields:
            fields = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Неизвестные критерии поиска: {fields}")

        return [aeroplane for aeroplane in aeroplanes if self._matches(aeroplane, criteria)]

    def delete_aeroplane(self, aeroplane: Aeroplane | str) -> bool:
        if isinstance(aeroplane, Aeroplane):
            identity = self._identity(aeroplane)
        elif isinstance(aeroplane, str) and aeroplane.strip():
            identity = aeroplane.strip().casefold()
        else:
            raise TypeError("Для удаления передайте Aeroplane или непустой идентификатор")

        data = self._read_data()
        filtered = [item for item in data if self._identity_from_dict(item) != identity]
        deleted = len(filtered) != len(data)
        if deleted:
            self._write_data(filtered)
        return deleted

    @staticmethod
    def _identity(aeroplane: Aeroplane) -> str:
        return (aeroplane.icao24 or aeroplane.callsign).casefold()

    @staticmethod
    def _identity_from_dict(item: dict[str, Any]) -> str:
        return str(item.get("icao24") or item.get("callsign") or "").casefold()

    @staticmethod
    def _matches(aeroplane: Aeroplane, criteria: Mapping[str, object]) -> bool:
        for field, expected in criteria.items():
            actual = getattr(aeroplane, field)
            if isinstance(actual, str) and isinstance(expected, str):
                if actual.casefold() != expected.strip().casefold():
                    return False
            elif actual != expected:
                return False
        return True

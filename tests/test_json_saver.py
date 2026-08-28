from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.aeroplane import Aeroplane
from src.base_storage import BaseStorage
from src.exceptions import StorageError
from src.json_saver import JSONSaver


def test_json_saver_inherits_storage_interface(tmp_path: Path) -> None:
    assert issubclass(JSONSaver, BaseStorage)
    assert JSONSaver(tmp_path / "new" / "aircraft.json").get_aeroplanes() == []


def test_add_and_get_aeroplanes(tmp_path: Path, aeroplanes: list[Aeroplane]) -> None:
    path = tmp_path / "aircraft.json"
    saver = JSONSaver(path)

    saver.add_aeroplane(aeroplanes[0])
    saver.add_aeroplane(aeroplanes[1])

    restored = saver.get_aeroplanes()
    assert [item.to_dict() for item in restored] == [item.to_dict() for item in aeroplanes[:2]]
    assert json.loads(path.read_text(encoding="utf-8"))[0]["origin_country"] == "France"


def test_add_updates_duplicate_by_icao24(tmp_path: Path) -> None:
    saver = JSONSaver(tmp_path / "aircraft.json")
    saver.add_aeroplane(Aeroplane("OLD", "France", 100, 1000, "abc123"))

    saver.add_aeroplane(Aeroplane("NEW", "France", 200, 2000, "abc123"))

    restored = saver.get_aeroplanes()
    assert len(restored) == 1
    assert restored[0].callsign == "NEW"


def test_get_filters_case_insensitively(tmp_path: Path, aeroplanes: list[Aeroplane]) -> None:
    saver = JSONSaver(tmp_path / "aircraft.json")
    for aeroplane in aeroplanes:
        saver.add_aeroplane(aeroplane)

    result = saver.get_aeroplanes({"origin_country": "france"})

    assert [item.callsign for item in result] == ["LOW100", "MID300"]
    with pytest.raises(ValueError, match="Неизвестные"):
        saver.get_aeroplanes({"unknown": "value"})


def test_delete_by_object_and_identifier(tmp_path: Path, aeroplanes: list[Aeroplane]) -> None:
    saver = JSONSaver(tmp_path / "aircraft.json")
    for aeroplane in aeroplanes[:2]:
        saver.add_aeroplane(aeroplane)

    assert saver.delete_aeroplane(aeroplanes[0])
    assert saver.delete_aeroplane("BBB222")
    assert saver.get_aeroplanes() == []
    assert not saver.delete_aeroplane("missing")


def test_storage_rejects_wrong_arguments(tmp_path: Path) -> None:
    saver = JSONSaver(tmp_path / "aircraft.json")

    with pytest.raises(TypeError, match="Aeroplane"):
        saver.add_aeroplane("invalid")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="удаления"):
        saver.delete_aeroplane(123)  # type: ignore[arg-type]


@pytest.mark.parametrize("content", ["not json", "{}", '[{"callsign": "broken"}]'])
def test_invalid_file_content_is_reported(tmp_path: Path, content: str) -> None:
    path = tmp_path / "aircraft.json"
    path.write_text(content, encoding="utf-8")
    saver = JSONSaver(path)

    with pytest.raises(StorageError):
        saver.get_aeroplanes()

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from src.aeroplane import StateVector
from src.base_api import BaseAPI, CountryBounds
from src.json_saver import JSONSaver
from src.user_interface import user_interaction


class FakeAPI(BaseAPI):
    def __init__(self, states: list[StateVector], error: Exception | None = None) -> None:
        self.states = states
        self.error = error

    def get_country_bounds(self, country: str) -> CountryBounds:
        return 0.0, 1.0, 0.0, 1.0

    def get_aeroplanes(self, country: str) -> list[StateVector]:
        if self.error:
            raise self.error
        return self.states


def _input_from(values: list[str]) -> tuple[Iterator[str], object]:
    answers = iter(values)

    def fake_input(prompt: str) -> str:
        return next(answers)

    return answers, fake_input


def test_user_interaction_combines_all_components(
    tmp_path: Path,
    state_vectors: list[StateVector],
) -> None:
    _, input_func = _input_from(["Spain", "wrong", "2", "united states", "1000 - 15000"])
    output: list[str] = []
    saver = JSONSaver(tmp_path / "aircraft.json")

    result = user_interaction(
        api=FakeAPI(state_vectors),
        storage=saver,
        input_func=input_func,  # type: ignore[arg-type]
        output_func=output.append,
    )

    assert [item.callsign for item in result] == ["UAL1621"]
    assert len(saver.get_aeroplanes()) == 2
    assert output[0] == "Введите положительное целое число."
    assert output[1] == "Найдено самолетов в воздушном пространстве: 2"
    assert output[2].startswith("1. UAL1621")


def test_user_interaction_handles_expected_error(tmp_path: Path) -> None:
    _, input_func = _input_from(["Spain", "1", "", ""])
    output: list[str] = []

    result = user_interaction(
        api=FakeAPI([], ValueError("bad request")),
        storage=JSONSaver(tmp_path / "aircraft.json"),
        input_func=input_func,  # type: ignore[arg-type]
        output_func=output.append,
    )

    assert result == []
    assert output == ["Не удалось выполнить запрос: bad request"]

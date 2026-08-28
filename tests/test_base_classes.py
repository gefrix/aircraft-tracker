import pytest

from src.base_api import BaseAPI
from src.base_storage import BaseStorage


def test_base_api_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseAPI()  # type: ignore[abstract]


def test_base_storage_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseStorage()  # type: ignore[abstract]

"""Unit test for CatalogueService happy path with a mocked client.

Covers parsing of items and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.catalogues.service import CatalogueService


class DummyResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.cached_indicator = "💾"

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._data


class DummyClient:
    def get(self, url: str, **kwargs: Any) -> NumistaResponse:  # type: ignore[override]
        assert url == "/catalogues"
        return DummyResponse({
            "catalogues": [
                {"id": 1, "code": "KM", "title": "Krause-Mishler", "author": "Test"},
                {"id": 2, "code": "SC", "title": "Standard Catalog", "author": None},
            ]
        })  # type: ignore[return-value]


def test_get_catalogues_parses_items() -> None:
    service = CatalogueService(DummyClient())
    items = service.get_catalogues()
    assert len(items) == 2
    assert items[0].code == "KM"
    assert items[1].title == "Standard Catalog"

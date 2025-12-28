"""Unit tests for MintService happy path with mocked client.

Covers get_mints conversion and logging path without network calls.
"""

from typing import Any

from numistalib.client import NumistaResponse
from numistalib.services.mints.service import MintService


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
        assert url == "/mints"
        return DummyResponse({
            "mints": [
                {
                    "numista_id": 1,
                    "name": "Test Mint",
                    "code": "TM",
                    "place": "Test City",
                }
            ]
        })  # type: ignore[return-value]


def test_get_mints_parses_items() -> None:
    service = MintService(DummyClient())
    items = service.get_mints(lang="en")
    assert len(items) == 1
    assert items[0].name == "Test Mint"
    assert items[0].code == "TM"

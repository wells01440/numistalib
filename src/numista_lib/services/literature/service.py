"""Literature service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from numista_lib import logger
from numista_lib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numista_lib.models import Publication
from numista_lib.services.literature.base import LiteratureServiceBase


class LiteratureService(LiteratureServiceBase):
    """Unified literature service supporting both sync and async clients."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize literature service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def _to_models(
        self, items: list[Mapping[str, Any]], **kwargs: Any
    ) -> list[Publication]:
        """Convert API response items to Publication models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Publication]
            Parsed publication models
        """
        publications: list[Publication] = []
        for item in items:
            publications.append(
                Publication(
                    numista_id=cast(int, item["id"]),
                    publication_type=cast(str, item.get("type", "unknown")),
                    title=cast(str, item["title"]),
                    authors=cast(list[str] | None, item.get("authors")),
                    year=cast(int | None, item.get("year")),
                    publisher=cast(str | None, item.get("publisher")),
                    isbn=cast(str | None, item.get("isbn")),
                    pages=cast(str | None, item.get("pages")),
                    url=cast(str | None, item.get("url")),
                )
            )
        return publications

    def get_publication(self, publication_id: int) -> Publication:
        """Get publication details by ID.

        Parameters
        ----------
        publication_id : int
            Numista publication ID

        Returns
        -------
        Publication
            Publication details

        Examples
        --------
        >>> service = LiteratureService(client)
        >>> pub = service.get_publication(123)
        >>> print(pub.title)
        """
        logger.debug(f"Fetching publication {publication_id}")
        response = cast(NumistaResponse, self._client.get(f"/publications/{publication_id}"))
        response.raise_for_status()
        self._track_response(response)

        # Single publication, not wrapped in array
        data = cast(Mapping[str, Any], response.json())
        return self._to_models([data])[0]

    async def get_publication_async(self, publication_id: int) -> Publication:
        """Get publication details by ID (async).

        Parameters
        ----------
        publication_id : int
            Numista publication ID

        Returns
        -------
        Publication
            Publication details

        Examples
        --------
        >>> service = LiteratureService(async_client)
        >>> pub = await service.get_publication_async(123)
        >>> print(pub.title)
        """
        logger.debug(f"Fetching publication {publication_id} (async)")
        response = await self._aget(f"/publications/{publication_id}")
        response.raise_for_status()
        self._track_response(response)

        # Single publication, not wrapped in array
        data = cast(Mapping[str, Any], response.json())
        return self._to_models([data])[0]


__all__ = ["LiteratureService"]

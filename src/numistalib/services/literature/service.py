"""Literature service implementation."""

from collections.abc import Mapping
from typing import Any, Literal, cast

from pydantic import HttpUrl
from pydantic import TypeAdapter

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models import Contributor, PartOf, Publication, PublicationPlace, Publisher
from numistalib.services.literature.base import LiteratureServiceBase

_HTTP_URL_ADAPTER: TypeAdapter[HttpUrl] = TypeAdapter(HttpUrl)
_HTTP_URL_LIST_ADAPTER: TypeAdapter[list[HttpUrl]] = TypeAdapter(list[HttpUrl])


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

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
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
            raw_publishers = cast(list[Any], item.get("publishers", []))
            publishers = (
                [
                    Publisher(**cast(Mapping[str, Any], p))
                    if isinstance(p, Mapping)
                    else Publisher(name=cast(str, p))
                    for p in raw_publishers
                ]
                or None
            )

            raw_publication_places = cast(list[Any], item.get("publication_places", []))
            publication_places = (
                [
                    PublicationPlace(**cast(Mapping[str, Any], pp))
                    if isinstance(pp, Mapping)
                    else PublicationPlace(name=cast(str, pp))
                    for pp in raw_publication_places
                ]
                or None
            )

            raw_part_of = item.get("part_of")
            part_of: list[PartOf] | None
            if raw_part_of is None:
                part_of = None
            elif isinstance(raw_part_of, list):
                part_of = [PartOf(**cast(Mapping[str, Any], po)) for po in raw_part_of if isinstance(po, Mapping)] or None
            elif isinstance(raw_part_of, Mapping):
                part_of = [PartOf(**cast(Mapping[str, Any], raw_part_of))]
            else:
                part_of = None

            raw_homepage_url = item.get("homepage_url")
            homepage_url = (
                _HTTP_URL_ADAPTER.validate_python(raw_homepage_url)
                if isinstance(raw_homepage_url, str) and raw_homepage_url.strip()
                else None
            )

            raw_download_urls = item.get("download_urls")
            download_urls = (
                _HTTP_URL_LIST_ADAPTER.validate_python(raw_download_urls)
                if isinstance(raw_download_urls, list) and raw_download_urls
                else None
            )

            raw_url = item.get("url")
            url = (
                _HTTP_URL_ADAPTER.validate_python(raw_url)
                if isinstance(raw_url, str) and raw_url.strip()
                else None
            )

            publications.append(
                Publication(
                    id=cast(str, str(item["id"])),
                    type=cast(Literal["volume", "article", "volume_group", "article_group"], item.get("type", "volume")),
                    title=cast(str, item["title"]),
                    translated_title=cast(str | None, item.get("translated_title")),
                    volume_number=cast(str | None, item.get("volume_number")),
                    subtitle=cast(str | None, item.get("subtitle")),
                    translated_subtitle=cast(str | None, item.get("translated_subtitle")),
                    edition=cast(str | None, item.get("edition")),
                    languages=cast(list[str] | None, item.get("languages")),
                    page_count=cast(int | None, item.get("page_count")),
                    cover=cast(Literal["softcover", "hardcover", "spiral", "hidden_spiral"] | None, item.get("cover")),
                    isbn10=cast(str | None, item.get("isbn10")),
                    isbn13=cast(str | None, item.get("isbn13")),
                    issn=cast(str | None, item.get("issn")),
                    oclc_number=cast(str | None, item.get("oclc_number")),
                    contributors=[Contributor(**c) for c in item.get("contributors", [])] or None,
                    publishers=publishers,
                    publication_places=publication_places,
                    part_of=part_of,
                    bibliographical_notice=cast(str | None, item.get("bibliographical_notice")),
                    homepage_url=homepage_url,
                    download_urls=download_urls,
                    url=url,
                    year=cast(int | None, item.get("year")),
                    pages=cast(str | None, item.get("pages")),
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
        return self.to_models([data])[0]

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
        return self.to_models([data])[0]


__all__ = ["LiteratureService"]

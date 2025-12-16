"""Issuer service implementation."""

from collections.abc import AsyncGenerator, Mapping
from typing import Any, cast

import httpx
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from numista_lib import logger
from numista_lib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numista_lib.models.issuer import Issuer
from numista_lib.services.issuer.base import IssuerServiceBase


class PagedResponse(BaseModel):
    """Pagination response wrapper for issuers."""

    issuers: list[dict[str, Any]]
    next_url: str | None = None


class IssuerService(IssuerServiceBase):
    """Unified issuer service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "issuers"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize issuer service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def _to_models(
        self, items: list[Mapping[str, Any]], **kwargs: Any
    ) -> list[Issuer]:
        """Convert API response items to Issuer models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[Issuer]
            Parsed issuer models
        """
        issuers: list[Issuer] = []
        for item in items:
            parent = cast(Mapping[str, Any] | None, item.get("parent"))
            issuers.append(
                Issuer(
                    code=cast(str, item["code"]),
                    name=cast(str, item["name"]),
                    flag=cast(str | None, item.get("flag")) or "",
                    wikidata_id=cast(str | None, item.get("wikidata_id")),
                    level=cast(int | None, item.get("level")) or 1,
                    parent_code=cast(str | None, parent.get("code")) if parent else None,
                    parent_name=cast(str | None, parent.get("name")) if parent else None,
                )
            )
        return issuers

    def get_issuers(self, lang: str = "en", count: int | None = None) -> list[Issuer]:
        """Get the list of issuers.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page (API default is applied when None)

        Returns
        -------
        list[Issuer]
            List of issuers

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issuers(lang=%s, count=%s)", lang, count)

        params = self._build_params({"lang": lang}, count=count)

        response = cast(NumistaResponse, self._client.get("/issuers", params=params))
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        issuers = self._to_models(items)

        logger.info(f"Retrieved {len(issuers)} issuers {response.cached_indicator}")
        return issuers

    async def get_issuers_async(
        self, lang: str = "en", count: int | None = None
    ) -> list[Issuer]:
        """Get the list of issuers (async).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page (API default is applied when None)

        Returns
        -------
        list[Issuer]
            List of issuers

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issuers_async(lang=%s, count=%s)", lang, count)

        params = self._build_params({"lang": lang}, count=count)

        response = await self._aget("/issuers", params=params)
        response.raise_for_status()
        self._track_response(response)

        items = self._extract_items_from_response(response)
        issuers = self._to_models(items)

        logger.info(f"Retrieved {len(issuers)} issuers {response.cached_indicator}")
        return issuers

    @staticmethod
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _fetch_page(client: httpx.AsyncClient, url: str) -> PagedResponse:
        """Fetch a single page of issuers with retry logic.

        Parameters
        ----------
        client : httpx.AsyncClient
            Async HTTP client
        url : str
            Endpoint URL (full URL)

        Returns
        -------
        PagedResponse
            Parsed response with issuers and next_url

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return PagedResponse(
            issuers=data.get("issuers", []),
            next_url=data.get("next_url"),
        )

    async def paginated_issuers(
        self,
        lang: str = "en",
        limit: int = 50,
    ) -> AsyncGenerator[Issuer]:
        """Lazily iterate all issuers by following pagination links.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issuer
            Individual issuer records
        """
        logger.debug("→ paginated_issuers(lang=%s, limit=%s)", lang, limit)

        start_url = f"/issuers?lang={lang}&count={limit}"

        api_key = getattr(self._client, "api_key", None)
        base_url = getattr(self._client, "api_base_url", "https://api.numista.com/v3")
        if not api_key:
            raise ValueError("API key is required for pagination")

        async with httpx.AsyncClient(
            headers={"Numista-API-Key": api_key},
            timeout=30.0,
        ) as client:
            url: str | None = start_url
            page_count = 0

            while url:
                page_count += 1
                # Build full URL if it's a relative path
                full_url = url if url.startswith(("http://", "https://")) else f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                logger.debug(f"Fetching issuers page {page_count}: {full_url}")

                page = await self._fetch_page(client, full_url)

                for item in page.issuers:
                    parent = item.get("parent", {})
                    issuer = Issuer(
                        code=item["code"],
                        name=item["name"],
                        flag=item.get("flag") or "",
                        wikidata_id=item.get("wikidata_id"),
                        level=item.get("level", 1),
                        parent_code=parent.get("code") if parent else None,
                        parent_name=parent.get("name") if parent else None,
                    )
                    yield issuer

                url = page.next_url

            logger.info(
                f"Finished paginating through {page_count} pages of issuers"
            )

    async def get_issuers_paginated(
        self,
        lang: str = "en",
        limit: int = 50,
    ) -> AsyncGenerator[Issuer]:
        """Paginate through all issuers (alias for paginated_issuers).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issuer
            Individual issuer records
        """
        async for issuer in self.paginated_issuers(lang=lang, limit=limit):
            yield issuer


# Backward compatibility exports
IssuerServiceAsync = IssuerService

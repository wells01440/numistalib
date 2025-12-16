"""Issue service implementation."""

from collections.abc import AsyncGenerator, Mapping
from typing import Any, NotRequired, TypedDict, cast

import httpx
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from numista_lib import logger
from numista_lib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numista_lib.models.issues import Issue
from numista_lib.services.issues.base import IssueServiceBase


class IssuePagedResponse(BaseModel):
    """Pagination response wrapper for issues."""

    issues: list["IssueItem"]
    next_url: str | None = None


class IssueItem(TypedDict):
    """Typed dict representing a single issue item from API."""

    id: int
    is_dated: NotRequired[bool]
    year: NotRequired[int | None]
    gregorian_year: NotRequired[int | None]
    mint_letter: NotRequired[str | None]
    mintage: NotRequired[int | None]
    comment: NotRequired[str | None]


class IssueService(IssueServiceBase):
    """Unified issue service supporting both sync and async clients."""

    CLASS_ITEMS_KEY = "issues"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize issue service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def _to_models(
        self, items: list[Mapping[str, Any]], type_id: int | None = None, **kwargs: Any
    ) -> list[Issue]:
        """Convert API response items to Issue models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        type_id : int | None
            Numista type ID (required context)
        **kwargs : Any
            Additional context

        Returns
        -------
        list[Issue]
            Parsed issue models
        """
        if type_id is None:
            raise ValueError("type_id is required for issue conversion")

        issues: list[Issue] = []
        for item in items:
            issues.append(
                Issue(
                    numista_id=cast(int, item["id"]),
                    type_id=type_id,
                    is_dated=cast(bool | None, item.get("is_dated")) or False,
                    year=cast(int | None, item.get("year")),
                    gregorian_year=cast(int | None, item.get("gregorian_year")),
                    mint_letter=cast(str | None, item.get("mint_letter")),
                    mintage=cast(int | None, item.get("mintage")),
                    comment=cast(str | None, item.get("comment")),
                )
            )
        return issues

    def get_issues(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (single call).

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code

        Returns
        -------
        list[Issue]
            List of issues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issues(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(
            NumistaResponse,
            self._client.get(f"/types/{type_id}/issues", params=params),
        )
        response.raise_for_status()
        self._track_response(response)
        data = response.json()

        items = cast(list[Mapping[str, Any]], data) if isinstance(data, list) else cast(
            list[Mapping[str, Any]], data.get("issues", [])
        )
        issues = self._to_models(items, type_id=type_id)

        logger.info(
            f"Retrieved {len(issues)} issues for type {type_id} {response.cached_indicator}"
        )
        return issues

    def add_issue(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type.

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_data : Mapping[str, Any]
            Issue data payload
        lang : str | None
            Language code

        Returns
        -------
        Issue
            Created issue

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_issue(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(
            NumistaResponse,
            self._client.post(
                f"/types/{type_id}/issues", params=params, json=dict(issue_data)
            ),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        issue = self._to_models([data], type_id=type_id)[0]

        logger.info(
            f"Added issue {issue.numista_id} for type {type_id} {response.cached_indicator}"
        )
        return issue

    async def get_issues_async(self, type_id: int, lang: str = "en") -> list[Issue]:
        """Get all issues for a specific type (async).

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code

        Returns
        -------
        list[Issue]
            List of issues

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ get_issues_async(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._aget(f"/types/{type_id}/issues", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = response.json()

        items = cast(list[Mapping[str, Any]], data) if isinstance(data, list) else cast(
            list[Mapping[str, Any]], data.get("issues", [])
        )
        issues = self._to_models(items, type_id=type_id)

        logger.info(
            f"Retrieved {len(issues)} issues for type {type_id} {response.cached_indicator}"
        )
        return issues

    async def add_issue_async(
        self,
        type_id: int,
        issue_data: Mapping[str, Any],
        lang: str | None = None,
    ) -> Issue:
        """Add a new issue to a type (async).

        Parameters
        ----------
        type_id : int
            Numista type ID
        issue_data : Mapping[str, Any]
            Issue data payload
        lang : str | None
            Language code

        Returns
        -------
        Issue
            Created issue

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        logger.debug("→ add_issue_async(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._apost(
            f"/types/{type_id}/issues", params=params, json=dict(issue_data)
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        issue = self._to_models([data], type_id=type_id)[0]

        logger.info(
            f"Added issue {issue.numista_id} for type {type_id} {response.cached_indicator}"
        )
        return issue

    @staticmethod
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _fetch_page(client: httpx.AsyncClient, url: str) -> IssuePagedResponse:
        """Fetch a single page of issues with retry logic.

        Parameters
        ----------
        client : httpx.AsyncClient
            Async HTTP client
        url : str
            Endpoint URL

        Returns
        -------
        IssuePagedResponse
            Parsed response with issues and next_url

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        """
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return IssuePagedResponse(
                issues=cast(list[IssueItem], data),
                next_url=None,
            )
        return IssuePagedResponse(
            issues=cast(list[IssueItem], data.get("issues", [])),
            next_url=data.get("next_url"),
        )

    async def paginated_issues(
        self,
        type_id: int,
        lang: str = "en",
        limit: int = 100,
    ) -> AsyncGenerator[Issue]:
        """Lazily iterate issues by following pagination links.

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issue
            Individual issue records
        """
        logger.debug(
            "→ paginated_issues(type_id=%s, lang=%s, limit=%s)", type_id, lang, limit
        )

        start_url = f"/types/{type_id}/issues?lang={lang}&count={limit}"

        api_key = getattr(self._client, "api_key", None)
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
                logger.debug(f"Fetching issues page {page_count}: {url}")

                page = await self._fetch_page(client, url)

                for item in page.issues:
                    issue = Issue(
                        numista_id=item["id"],
                        type_id=type_id,
                        is_dated=item.get("is_dated", False),
                        year=item.get("year"),
                        gregorian_year=item.get("gregorian_year"),
                        mint_letter=item.get("mint_letter"),
                        mintage=item.get("mintage"),
                        comment=item.get("comment"),
                    )
                    yield issue

                url = page.next_url

            logger.info(f"Finished paginating through {page_count} pages of issues")

    async def get_issues_paginated(
        self,
        type_id: int,
        lang: str = "en",
        limit: int = 100,
    ) -> AsyncGenerator[Issue]:
        """Paginate through issues for a type (alias for paginated_issues).

        Parameters
        ----------
        type_id : int
            Numista type ID
        lang : str
            Language code
        limit : int
            Results per page (max 100)

        Yields
        ------
        Issue
            Individual issue records
        """
        async for issue in self.paginated_issues(type_id=type_id, lang=lang, limit=limit):
            yield issue


# Backward compatibility exports
IssueServiceAsync = IssueService

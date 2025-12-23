"""Type service implementation."""

from collections.abc import AsyncGenerator, Mapping
from dataclasses import dataclass
from typing import Any, cast

from pydantic import BaseModel

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services.types.base import (
    TypeBasicServiceBase,
    TypeFullServiceBase,
    TypeServiceBase,
)


@dataclass
class SearchParams:
    """Search parameters for type catalogue queries."""

    query: str | None = None
    issuer: str | None = None
    year: int | None = None
    category: str | None = None
    lang: str = "en"
    page: int = 1
    count: int = 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to API parameter dictionary.

        Returns
        -------
        dict[str, Any]
            Parameters dictionary for HTTP request
        """
        params: dict[str, Any] = {
            "lang": self.lang,
            "count": min(self.count, 100),
        }
        if self.page > 1:
            params["page"] = self.page
        if self.query:
            params["q"] = self.query
        if self.issuer:
            params["issuer"] = self.issuer
        if self.year:
            params["year"] = self.year
        if self.category:
            params["category"] = self.category
        return params

    def has_search_criteria(self) -> bool:
        """Check if at least one search criterion is provided.

        Returns
        -------
        bool
            True if any search criteria specified
        """
        return any([self.query, self.issuer, self.year, self.category])


class TypePagedResponse(BaseModel):
    """Pagination response wrapper for types search."""

    types: list[dict[str, Any]]
    next_url: str | None = None


class TypeBasicService(TypeBasicServiceBase):
    """Type search service returning TypeBasic models."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        super().__init__(client)

    def to_models(self, items: list[Mapping[str, Any]], **kwargs: Any) -> list[TypeBasic]:  # noqa: PLR6301, ARG002
        return [TypeBasic.model_validate(item) for item in items]

    def search_types(self, params: SearchParams) -> list[TypeBasic]:
        logger.debug(
            "→ search_types(query=%s, issuer=%s, year=%s, category=%s, page=%s)",
            params.query,
            params.issuer,
            params.year,
            params.category,
            params.page,
        )

        if not params.has_search_criteria():
            raise ValueError(
                "At least one search parameter (q, issuer, year, category) required"
            ) from None

        response = cast(
            NumistaResponse, self._client.get("/types", params=params.to_dict())
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        types_list = [TypeBasic.model_validate(item) for item in data.get("types", [])]

        logger.info(
            f"Retrieved {len(types_list)} types page {params.page} {response.cached_indicator}"
        )
        return types_list

    async def search_types_async(self, params: SearchParams) -> list[TypeBasic]:
        logger.debug(
            "→ search_types_async(query=%s, issuer=%s, year=%s, category=%s, page=%s)",
            params.query,
            params.issuer,
            params.year,
            params.category,
            params.page,
        )

        if not params.has_search_criteria():
            raise ValueError(
                "At least one search parameter (q, issuer, year, category) required"
            ) from None

        response = await self._aget("/types", params=params.to_dict())
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        types_list = [TypeBasic.model_validate(item) for item in data.get("types", [])]

        logger.info(
            f"Retrieved {len(types_list)} types page {params.page} {response.cached_indicator}"
        )
        return types_list

    async def paginated_search(self, params: SearchParams) -> AsyncGenerator[TypeBasic]:
        logger.debug(
            "→ paginated_search(query=%s, issuer=%s, year=%s, category=%s)",
            params.query,
            params.issuer,
            params.year,
            params.category,
        )

        if not params.has_search_criteria():
            raise ValueError(
                "At least one search parameter (q, issuer, year, category) required"
            ) from None

        page_num = 1
        while True:
            params.page = page_num
            logger.debug(f"Fetching types page {page_num}")

            response = await self._aget("/types", params=params.to_dict())
            response.raise_for_status()
            self._track_response(response)
            data = cast(Mapping[str, Any], response.json())

            types_list = [TypeBasic.model_validate(item) for item in data.get("types", [])]

            if not types_list:
                break

            for type_item in types_list:
                yield type_item

            if not data.get("next_url"):
                break

            page_num += 1

        logger.info(f"Finished paginating {page_num} pages of type results")

    async def search_types_paginated(
        self,
        query: str | None = None,
        issuer: str | None = None,
        year: int | None = None,
        category: str | None = None,
        limit: int = 50,
        lang: str = "en",
    ) -> AsyncGenerator[TypeBasic]:
        params = SearchParams(
            query=query,
            issuer=issuer,
            year=year,
            category=category,
            count=min(limit, 100),
            lang=lang,
        )
        async for type_item in self.paginated_search(params=params):
            yield type_item


class TypeFullService(TypeFullServiceBase):
    """Type detail service returning TypeFull models."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        super().__init__(client)

    def to_models(self, items: list[Mapping[str, Any]], **kwargs: Any) -> list[TypeFull]:  # noqa: PLR6301, ARG002
        return [TypeFull.model_validate(item) for item in items]

    def get_type(self, type_id: int, *, lang: str | None = None) -> TypeFull:
        logger.debug("→ get_type(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(NumistaResponse, self._client.get(f"/types/{type_id}", params=params))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        type_full = TypeFull.model_validate(data)

        logger.info(f"Retrieved type {type_id}: {type_full.title} {response.cached_indicator}")
        return type_full

    async def get_type_async(self, type_id: int, *, lang: str | None = None) -> TypeFull:
        logger.debug("→ get_type_async(type_id=%s, lang=%s)", type_id, lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._aget(f"/types/{type_id}", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        type_full = TypeFull.model_validate(data)

        logger.info(f"Retrieved type {type_id}: {type_full.title} {response.cached_indicator}")
        return type_full

    def add_type(self, type_data: dict[str, object], lang: str | None = None) -> TypeFull:
        logger.debug("→ add_type(lang=%s)", lang)

        params = self._build_params(lang=lang) if lang else None
        response = cast(NumistaResponse, self._client.post("/types", params=params, json=type_data))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        type_obj = TypeFull.model_validate(data)

        logger.info(f"Added type {type_obj.id} {response.cached_indicator}")
        return type_obj

    async def add_type_async(self, type_data: dict[str, object], lang: str | None = None) -> TypeFull:
        logger.debug("→ add_type_async(lang=%s)", lang)

        params = self._build_params(lang=lang) if lang else None
        response = await self._apost("/types", params=params, json=type_data)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        type_obj = TypeFull.model_validate(data)

        logger.info(f"Added type {type_obj.id} {response.cached_indicator}")
        return type_obj


class TypeService(TypeFullService, TypeBasicService, TypeServiceBase):  # type: ignore[misc]
    """Composite type service combining search (basic) and detail (full).

    Note: mypy reports to_models conflict between TypeBasicService (returns list[TypeBasic])
    and TypeFullService (returns list[TypeFull]). This is inherent to composite service design;
    each parent class uses its own to_models internally. Python MRO resolves correctly at runtime.
    """

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        super().__init__(client)

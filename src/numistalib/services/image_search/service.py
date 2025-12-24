"""Image Search service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from pydantic import HttpUrl

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.types import Country, TypeBasic
from numistalib.services.image_search.base import ImageSearchServiceBase


class ImageSearchService(ImageSearchServiceBase):
    """Unified image search service supporting both sync and async clients.

    This is a paid feature. See pricing page for details.
    """

    CLASS_ITEMS_KEY = "types"

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize image search service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any  # noqa: ARG002
    ) -> list[TypeBasic]:
        """Convert API response items to TypeBasic models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        **kwargs : Any
            Unused (for interface consistency)

        Returns
        -------
        list[TypeBasic]
            List of type models
        """
        types: list[TypeBasic] = []
        for item in items:
            issuer_obj = cast(Mapping[str, Any], item.get("issuer", {}))
            country_val = item.get("country", issuer_obj.get("country"))
            country_obj: Country | None = None
            if isinstance(country_val, Mapping):
                country_obj = cast(Country, country_val)
            elif country_val is not None:
                country_obj = cast(Country, country_val)

            obverse_url = item.get("obverse_thumbnail")
            reverse_url = item.get("reverse_thumbnail")
            
            types.append(
                TypeBasic(
                    id=cast(int, item["id"]),
                    title=cast(str, item["title"]),
                    category=cast(str, item["category"]),  # type: ignore[arg-type]
                    issuer=issuer_obj,  # type: ignore[arg-type]
                    country=country_obj,
                    min_year=cast(int | None, item.get("min_year")),
                    max_year=cast(int | None, item.get("max_year")),
                    obverse_thumbnail=HttpUrl(obverse_url) if obverse_url else None,
                    reverse_thumbnail=HttpUrl(reverse_url) if reverse_url else None,
                )
            )
        return types

    def search_by_image(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s).

        This is a paid feature.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys.
            Max 2 images. Max size 1024x1024 px.
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta, longer response time)

        Returns
        -------
        list[TypeBasic]
            List of matching types (up to 100)

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        ValueError
            If invalid image count or size
        """
        logger.debug(
            "→ search_by_image(image_count=%s, category=%s, lang=%s, experimental=%s)",
            len(images),
            category,
            lang,
            activate_experimental_features,
        )

        params = self._build_params(
            lang=lang,
            activate_experimental_features=activate_experimental_features or None,
        )

        payload: dict[str, object] = {"images": images}
        if category:
            payload["category"] = category

        response = cast(
            NumistaResponse,
            self._client.post("/search_by_image", params=params, json=payload),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))

        types = self.to_models(items)

        logger.info(
            f"Image search found {len(types)} matching types {response.cached_indicator}"
        )
        return types

    async def search_by_image_async(
        self,
        images: list[dict[str, str]],
        category: str | None = None,
        lang: str = "en",
        activate_experimental_features: bool = False,
    ) -> list[TypeBasic]:
        """Search catalogue by image(s) (async).

        This is a paid feature.

        Parameters
        ----------
        images : list[dict]
            List of image objects with 'mime_type' and 'image_data' keys.
            Max 2 images. Max size 1024x1024 px.
        category : str | None
            Filter by category (coin, banknote, exonumia)
        lang : str
            Language code
        activate_experimental_features : bool
            Enable experimental features (beta, longer response time)

        Returns
        -------
        list[TypeBasic]
            List of matching types (up to 100)

        Raises
        ------
        httpx.HTTPStatusError
            If API returns error
        ValueError
            If invalid image count or size
        """
        logger.debug(
            "→ search_by_image_async(image_count=%s, category=%s, lang=%s, experimental=%s)",
            len(images),
            category,
            lang,
            activate_experimental_features,
        )

        params = self._build_params(
            lang=lang,
            activate_experimental_features=activate_experimental_features or None,
        )

        payload: dict[str, object] = {"images": images}
        if category:
            payload["category"] = category

        response = await self._apost("/search_by_image", params=params, json=payload)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))

        types = self.to_models(items)

        logger.info(
            f"Image search found {len(types)} matching types {response.cached_indicator}"
        )
        return types


# Backward compatibility exports
ImageSearchServiceAsync = ImageSearchService

"""Abstract base classes for Numista services."""

from abc import ABC, abstractmethod
from collections.abc import Coroutine, Mapping
from typing import Any, cast

from numista_lib import logger
from numista_lib.client import (
    CACHE_MISS_ICON,
    AsyncClientProtocol,
    NumistaResponse,
    SyncClientProtocol,
)


class BaseService(ABC):
    """Abstract base service class for all Numista services.

    Enforces strict patterns for:
    - Client injection via duck-typing
    - Converting raw data to typed models
    - Centralized HTTP error handling
    - Consistent caching and logging

    All concrete services must implement model conversion logic.
    """

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize base service with HTTP client.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client conforming to the sync or async protocol
        """
        self._client: SyncClientProtocol | AsyncClientProtocol = client
        self._last_response: NumistaResponse | None = None
        logger.debug(f"Initialized {self.__class__.__name__} service")

    async def _aget(self, url: str, **kwargs: Any) -> NumistaResponse:
        """Unified async GET that supports both sync and async clients.

        Returns NumistaResponse, awaiting if the client is async.
        """
        result: NumistaResponse | Coroutine[Any, Any, NumistaResponse] = self._client.get(url, **kwargs)
        if isinstance(result, NumistaResponse):
            self._last_response = result
            return result
        resp = await result
        self._last_response = resp
        return resp

    async def _apost(self, url: str, **kwargs: Any) -> NumistaResponse:
        result: NumistaResponse | Coroutine[Any, Any, NumistaResponse] = self._client.post(url, **kwargs)
        if isinstance(result, NumistaResponse):
            self._last_response = result
            return result
        resp = await result
        self._last_response = resp
        return resp

    async def _apatch(self, url: str, **kwargs: Any) -> NumistaResponse:
        result: NumistaResponse | Coroutine[Any, Any, NumistaResponse] = self._client.patch(url, **kwargs)
        if isinstance(result, NumistaResponse):
            self._last_response = result
            return result
        resp = await result
        self._last_response = resp
        return resp

    async def _aput(self, url: str, **kwargs: Any) -> NumistaResponse:
        result: NumistaResponse | Coroutine[Any, Any, NumistaResponse] = self._client.put(url, **kwargs)
        if isinstance(result, NumistaResponse):
            self._last_response = result
            return result
        resp = await result
        self._last_response = resp
        return resp

    async def _adelete(self, url: str, **kwargs: Any) -> NumistaResponse:
        result: NumistaResponse | Coroutine[Any, Any, NumistaResponse] = self._client.delete(url, **kwargs)
        if isinstance(result, NumistaResponse):
            self._last_response = result
            return result
        resp = await result
        self._last_response = resp
        return resp

    @property
    def last_cache_indicator(self) -> str:
        """Get the cache indicator for the last response.

        Returns
        -------
        str
            Cache hit (💾) or cache miss (🌐) indicator
        """
        if self._last_response is None:
            return str(CACHE_MISS_ICON)
        return self._last_response.cached_indicator

    def _track_response(self, response: NumistaResponse) -> None:
        """Track the last API response for cache indicator access.

        Parameters
        ----------
        response : NumistaResponse
            The response to track
        """
        self._last_response = response

    @abstractmethod
    def _to_models(self, items: list[Mapping[str, Any]], **kwargs: Any) -> list[Any]:
        """Convert raw API items to typed domain models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw items from API response
        **kwargs : Any
            Service-specific conversion context (e.g., parent IDs)

        Returns
        -------
        list[Any]
            List of typed domain models
        """
        pass

    @staticmethod
    def _build_params(
        base: dict[str, Any] | None = None, **optional: Any
    ) -> dict[str, Any] | None:
        """Safely build parameter dict, excluding None values.

        Parameters
        ----------
        base : dict[str, Any] | None
            Base parameters (e.g., {'lang': 'en'})
        **optional
            Optional parameters to add if not None

        Returns
        -------
        dict[str, Any] | None
            Merged parameters or None if empty
        """
        params = dict(base) if base else {}
        for key, value in optional.items():
            if value is not None:
                params[key] = value
        return params if params else None


class SimpleListService(BaseService):
    """Base for endpoints returning a simple list of items in a single key.

    Used for endpoints like:
    - /catalogues → {"catalogues": [...]}
    - /mints → {"mints": [...]}

    Subclasses must:
    1. Define CLASS_ITEMS_KEY (e.g., "catalogues")
    2. Implement _to_models() to convert raw items
    """

    CLASS_ITEMS_KEY: str = "items"

    def _extract_items_from_response(
        self, response: NumistaResponse
    ) -> list[Mapping[str, Any]]:
        """Extract items list from standard response format.

        Parameters
        ----------
        response : NumistaResponse
            API response

        Returns
        -------
        list[Mapping[str, Any]]
            Raw items from response
        """
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))
        return items


class NestedResourceService(BaseService):
    """Base for endpoints with path parameters creating nested resources.

    Used for endpoints like:
    - /types/{type_id}/issues → {"issues": [...]}
    - /types/{type_id}/issues/{issue_id}/prices → {"prices": [...]}

    Subclasses must:
    1. Define CLASS_ITEMS_KEY
    2. Implement _to_models() with required context parameters
    """

    CLASS_ITEMS_KEY: str = "items"

    def _extract_items_from_response(
        self, response: NumistaResponse
    ) -> list[Mapping[str, Any]]:
        """Extract items from nested resource response.

        Parameters
        ----------
        response : NumistaResponse
            API response

        Returns
        -------
        list[Mapping[str, Any]]
            Raw items from response
        """
        data = cast(Mapping[str, Any], response.json())
        items = cast(list[Mapping[str, Any]], data.get(self.CLASS_ITEMS_KEY, []))
        return items


class EntityService(BaseService):
    """Base for single-entity endpoints.

    Used for endpoints like:
    - /users/{user_id} → {"user": {...}}
    - /types/{type_id} → {...}

    Subclasses implement _to_models() for single-item conversion.
    """

    def _to_models(
        self, items: list[Mapping[str, Any]], **kwargs: Any
    ) -> list[Any]:
        """Convert single entity (wrapped in list for interface consistency).

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Single-item list containing entity data
        **kwargs : Any
            Conversion context

        Returns
        -------
        list[Any]
            Single-item list with converted entity
        """
        if not items:
            return []
        return [self._convert_entity(items[0], **kwargs)]

    def _convert_entity(self, item: Mapping[str, Any], **kwargs: Any) -> Any:
        """Convert single entity to model.

        Parameters
        ----------
        item : Mapping[str, Any]
            Raw entity data
        **kwargs : Any
            Conversion context

        Returns
        -------
        Any
            Typed domain model
        """
        return self._to_models([item], **kwargs)[0]

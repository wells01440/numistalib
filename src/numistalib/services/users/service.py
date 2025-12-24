"""User service implementation."""

from collections.abc import Mapping
from typing import Any, cast

from pydantic import HttpUrl

from numistalib import logger
from numistalib.client import AsyncClientProtocol, NumistaResponse, SyncClientProtocol
from numistalib.models.collections import CollectedItem
from numistalib.models.users import User
from numistalib.services.users.base import UserServiceBase


class UserService(UserServiceBase):
    """Unified user service supporting both sync and async clients."""

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize user service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(  # noqa: PLR6301
        self, items: list[Mapping[str, Any]], **kwargs: Any
    ) -> list[User]:
        """Convert API response items to User models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items (single item)
        **kwargs : Any
            Optional context (e.g., user_id fallback when payload omits id)

        Returns
        -------
        list[User]
            List with single User model
        """
        user_id_fallback = cast(int | None, kwargs.get("user_id"))
        users: list[User] = []
        for item in items:
            try:
                username = cast(str, item["username"])
            except KeyError as err:
                raise ValueError("User payload missing required field 'username'") from err

            item_id = cast(int | None, item.get("id"))
            user_id = item_id if item_id is not None else user_id_fallback
            if user_id is None:
                raise ValueError("User payload missing required field 'id' and no fallback was provided")

            avatar_url = item.get("avatar")
            users.append(
                User(
                    id=user_id,
                    username=username,
                    avatar=HttpUrl(avatar_url) if avatar_url else None,
                    country_code=cast(str | None, item.get("country_code")),
                    member_since=cast(str | None, item.get("member_since")),
                )
            )
        return users

    def get_user(self, user_id: int) -> User:
        """Get details about a specific user.

        Supports both sync and async clients via duck-typing.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_user(user_id=%s)", user_id)

        response = cast(NumistaResponse, self._client.get(f"/users/{user_id}"))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        payload = cast(Mapping[str, Any], data.get("user", data))
        user = self.to_models([payload], user_id=user_id)[0]

        logger.info(f"Retrieved user {user_id}: {user.username} {response.cached_indicator}")
        return user

    def get_collections(self, user_id: int) -> list[dict[str, Any]]:
        """Get list of collections for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[dict[str, Any]]
            List of collection objects

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_collections(user_id=%s)", user_id)

        response = cast(NumistaResponse, self._client.get(f"/users/{user_id}/collections"))
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        collections: list[dict[str, Any]] = data.get("collections", [])

        logger.info(
            f"Retrieved {len(collections)} collections for user {user_id} {response.cached_indicator}"
        )
        return collections

    def get_collected_items(
        self,
        user_id: int,
        category: str | None = None,
        type_id: int | None = None,
        collection_id: int | None = None,
    ) -> list[CollectedItem]:
        """Get collected items for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID
        category : str | None
            Filter by category (coin, banknote, exonumia)
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug(
            "→ get_collected_items(user_id=%s, category=%s, type_id=%s, collection_id=%s)",
            user_id,
            category,
            type_id,
            collection_id,
        )

        params = self._build_params(category=category, type=type_id, collection=collection_id)

        response = cast(
            NumistaResponse,
            self._client.get(f"/users/{user_id}/collected_items", params=params),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        raw_items = cast(
            list[Mapping[str, Any]],
            data.get("items", data.get("collected_items", [])),
        )
        items_list = [CollectedItem.model_validate(item) for item in raw_items]

        logger.info(
            f"Retrieved {len(items_list)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items_list

    def get_collected_item(self, user_id: int, item_id: int) -> CollectedItem:
        """Get a specific collected item for a user."""
        logger.debug("→ get_collected_item(user_id=%s, item_id=%s)", user_id, item_id)

        response = cast(
            NumistaResponse,
            self._client.get(f"/users/{user_id}/collected_items/{item_id}"),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Retrieved collected item {item_id} for user {user_id} {response.cached_indicator}"
        )
        return item

    def add_collected_item(self, user_id: int, payload: dict[str, object]) -> CollectedItem:
        """Add an item to the user's collection."""
        logger.debug("→ add_collected_item(user_id=%s)", user_id)

        response = cast(
            NumistaResponse,
            self._client.post(f"/users/{user_id}/collected_items", json=payload),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Added collected item {item.id} for user {user_id} {response.cached_indicator}"
        )
        return item

    def edit_collected_item(
        self,
        user_id: int,
        item_id: int,
        payload: dict[str, object],
    ) -> CollectedItem:
        """Edit an item in the user's collection."""
        logger.debug("→ edit_collected_item(user_id=%s, item_id=%s)", user_id, item_id)

        response = cast(
            NumistaResponse,
            self._client.patch(f"/users/{user_id}/collected_items/{item_id}", json=payload),
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Edited collected item {item_id} for user {user_id} {response.cached_indicator}"
        )
        return item

    def delete_collected_item(self, user_id: int, item_id: int) -> None:
        """Delete an item from the user's collection."""
        logger.debug("→ delete_collected_item(user_id=%s, item_id=%s)", user_id, item_id)

        response = cast(
            NumistaResponse,
            self._client.delete(f"/users/{user_id}/collected_items/{item_id}"),
        )
        response.raise_for_status()
        self._track_response(response)
        logger.info(
            f"Deleted collected item {item_id} for user {user_id} {response.cached_indicator}"
        )

    async def get_user_async(self, user_id: int) -> User:
        """Get details about a specific user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_user_async(user_id=%s)", user_id)

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        payload = cast(Mapping[str, Any], data.get("user", data))
        user = self.to_models([payload], user_id=user_id)[0]

        logger.info(f"Retrieved user {user_id}: {user.username} {response.cached_indicator}")
        return user

    async def get_collections_async(self, user_id: int) -> list[dict[str, Any]]:
        """Get list of collections for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        list[dict[str, Any]]
            List of collection objects

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug("→ get_collections_async(user_id=%s)", user_id)

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}/collections")
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        collections: list[dict[str, Any]] = data.get("collections", [])

        logger.info(
            f"Retrieved {len(collections)} collections for user {user_id} {response.cached_indicator}"
        )
        return collections

    async def get_collected_items_async(
        self,
        user_id: int,
        category: str | None = None,
        type_id: int | None = None,
        collection_id: int | None = None,
    ) -> list[CollectedItem]:
        """Get collected items for a user (async).

        Parameters
        ----------
        user_id : int
            Numista user ID
        category : str | None
            Filter by category (coin, banknote, exonumia)
        type_id : int | None
            Filter by type ID
        collection_id : int | None
            Filter by collection ID

        Returns
        -------
        list[CollectedItem]
            List of collected items

        Raises
        ------
        httpx.HTTPStatusError
            If user not found or API error
        """
        logger.debug(
            "→ get_collected_items_async(user_id=%s, category=%s, type_id=%s, collection_id=%s)",
            user_id,
            category,
            type_id,
            collection_id,
        )

        params = self._build_params(category=category, type=type_id, collection=collection_id)

        response = await cast(AsyncClientProtocol, self._client).get(f"/users/{user_id}/collected_items", params=params)
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        raw_items = cast(
            list[Mapping[str, Any]],
            data.get("items", data.get("collected_items", [])),
        )
        items_list = [CollectedItem.model_validate(item) for item in raw_items]

        logger.info(
            f"Retrieved {len(items_list)} collected items for user {user_id} {response.cached_indicator}"
        )
        return items_list

    async def get_collected_item_async(self, user_id: int, item_id: int) -> CollectedItem:
        """Get a specific collected item for a user (async)."""
        logger.debug("→ get_collected_item_async(user_id=%s, item_id=%s)", user_id, item_id)

        response = await cast(AsyncClientProtocol, self._client).get(
            f"/users/{user_id}/collected_items/{item_id}"
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Retrieved collected item {item_id} for user {user_id} {response.cached_indicator}"
        )
        return item

    async def add_collected_item_async(self, user_id: int, payload: dict[str, object]) -> CollectedItem:
        """Add an item to the user's collection (async)."""
        logger.debug("→ add_collected_item_async(user_id=%s)", user_id)

        response = await cast(AsyncClientProtocol, self._client).post(
            f"/users/{user_id}/collected_items",
            json=payload,
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Added collected item {item.id} for user {user_id} {response.cached_indicator}"
        )
        return item

    async def edit_collected_item_async(
        self,
        user_id: int,
        item_id: int,
        payload: dict[str, object],
    ) -> CollectedItem:
        """Edit an item in the user's collection (async)."""
        logger.debug("→ edit_collected_item_async(user_id=%s, item_id=%s)", user_id, item_id)

        response = await cast(AsyncClientProtocol, self._client).patch(
            f"/users/{user_id}/collected_items/{item_id}",
            json=payload,
        )
        response.raise_for_status()
        self._track_response(response)
        data = cast(Mapping[str, Any], response.json())

        item = CollectedItem.model_validate(data)
        logger.info(
            f"Edited collected item {item_id} for user {user_id} {response.cached_indicator}"
        )
        return item

    async def delete_collected_item_async(self, user_id: int, item_id: int) -> None:
        """Delete an item from the user's collection (async)."""
        logger.debug("→ delete_collected_item_async(user_id=%s, item_id=%s)", user_id, item_id)

        response = await cast(AsyncClientProtocol, self._client).delete(
            f"/users/{user_id}/collected_items/{item_id}"
        )
        response.raise_for_status()
        self._track_response(response)
        logger.info(
            f"Deleted collected item {item_id} for user {user_id} {response.cached_indicator}"
        )


# Backward compatibility exports
UserServiceAsync = UserService

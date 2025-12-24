"""Abstract base classes for User service."""

from abc import abstractmethod
from typing import Any, ClassVar

from numistalib.models import CollectedItem, User
from numistalib.services.base import EntityService


class UserServiceBase(EntityService):
    """Abstract interface for user service operations.

    Enforces both sync and async implementations for all user queries.
    """

    MODEL_USER: ClassVar[type[User]] = User
    MODEL_COLLECTED_ITEM: ClassVar[type[CollectedItem]] = CollectedItem

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        """Get details about a specific user.

        Parameters
        ----------
        user_id : int
            Numista user ID

        Returns
        -------
        User
            User profile details
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
    def get_collected_item(self, user_id: int, item_id: int) -> CollectedItem:
        """Get a specific collected item for a user.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID

        Returns
        -------
        CollectedItem
            Collected item details
        """
        pass

    @abstractmethod
    def add_collected_item(self, user_id: int, payload: dict[str, object]) -> CollectedItem:
        """Add an item to the user's collection.

        Parameters
        ----------
        user_id : int
            Numista user ID
        payload : dict[str, object]
            Request body matching the API schema for adding a collected item

        Returns
        -------
        CollectedItem
            Created collected item
        """
        pass

    @abstractmethod
    def edit_collected_item(
        self,
        user_id: int,
        item_id: int,
        payload: dict[str, object],
    ) -> CollectedItem:
        """Edit a collected item in the user's collection.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID
        payload : dict[str, object]
            Partial update payload (only provided fields are updated)

        Returns
        -------
        CollectedItem
            Updated collected item
        """
        pass

    @abstractmethod
    def delete_collected_item(self, user_id: int, item_id: int) -> None:
        """Delete a collected item from the user's collection.

        Parameters
        ----------
        user_id : int
            Numista user ID
        item_id : int
            Collected item ID
        """
        pass

    @abstractmethod
    async def get_collected_item_async(self, user_id: int, item_id: int) -> CollectedItem:
        """Get a specific collected item for a user (async)."""
        pass

    @abstractmethod
    async def add_collected_item_async(
        self, user_id: int, payload: dict[str, object]
    ) -> CollectedItem:
        """Add an item to the user's collection (async)."""
        pass

    @abstractmethod
    async def edit_collected_item_async(
        self,
        user_id: int,
        item_id: int,
        payload: dict[str, object],
    ) -> CollectedItem:
        """Edit a collected item (async)."""
        pass

    @abstractmethod
    async def delete_collected_item_async(self, user_id: int, item_id: int) -> None:
        """Delete a collected item (async)."""
        pass

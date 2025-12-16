"""Abstract base classes for Literature service."""

from abc import abstractmethod
from typing import ClassVar

from numista_lib.models import Publication
from numista_lib.services.base import BaseService


class LiteratureServiceBase(BaseService):
    """Abstract interface for literature service operations.

    Enforces both sync and async implementations for publication queries.
    """

    MODEL: ClassVar[type[Publication]] = Publication

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass


__all__ = ["LiteratureServiceBase"]

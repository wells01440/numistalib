"""Abstract base classes for Issuer service."""

from abc import abstractmethod
from typing import ClassVar

from numista_lib.models import Issuer
from numista_lib.services.base import SimpleListService


class IssuerServiceBase(SimpleListService):
    """Abstract interface for issuer service operations.

    Enforces both sync and async implementations for all issuer queries.
    Pagination is supported via paginated_issuers async generator method.
    """

    MODEL: ClassVar[type[Issuer]] = Issuer

    @abstractmethod
    def get_issuers(self, lang: str = "en", count: int | None = None) -> list[Issuer]:
        """Get the list of issuers.

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page

        Returns
        -------
        list[Issuer]
            List of issuers
        """
        pass

    @abstractmethod
    async def get_issuers_async(
        self, lang: str = "en", count: int | None = None
    ) -> list[Issuer]:
        """Get the list of issuers (async).

        Parameters
        ----------
        lang : str
            Language code (en, es, fr)
        count : int | None
            Optional max results per page

        Returns
        -------
        list[Issuer]
            List of issuers
        """
        pass

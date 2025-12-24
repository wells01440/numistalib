"""Services for Numista API endpoints.

Note
----
This module intentionally avoids eagerly importing all service implementations.
Eager imports can create circular dependencies with the CLI and model layers.
"""

# Standard library
from importlib import import_module
from typing import TYPE_CHECKING

# Local
from numistalib.services.base import BaseService

if TYPE_CHECKING:
    from numistalib.services.catalogues import CatalogueService
    from numistalib.services.collections import CollectionService
    from numistalib.services.image_search import ImageSearchService
    from numistalib.services.issuer import IssuerService
    from numistalib.services.issues import IssueService
    from numistalib.services.literature import LiteratureService
    from numistalib.services.mints import MintService
    from numistalib.services.oauth import OAuthService
    from numistalib.services.prices import PriceService
    from numistalib.services.types import TypeBasicService, TypeFullService, TypeService
    from numistalib.services.users import UserService

__all__ = [
    "BaseService",
    "CatalogueService",
    "CollectionService",
    "ImageSearchService",
    "IssueService",
    "IssuerService",
    "LiteratureService",
    "MintService",
    "OAuthService",
    "PriceService",
    "TypeBasicService",
    "TypeFullService",
    "TypeService",
    "UserService",
]


_EXPORTS: dict[str, str] = {
    "CatalogueService": "numistalib.services.catalogues",
    "CollectionService": "numistalib.services.collections",
    "ImageSearchService": "numistalib.services.image_search",
    "IssuerService": "numistalib.services.issuer",
    "IssueService": "numistalib.services.issues",
    "LiteratureService": "numistalib.services.literature",
    "MintService": "numistalib.services.mints",
    "OAuthService": "numistalib.services.oauth",
    "PriceService": "numistalib.services.prices",
    "TypeBasicService": "numistalib.services.types",
    "TypeFullService": "numistalib.services.types",
    "TypeService": "numistalib.services.types",
    "UserService": "numistalib.services.users",
}


def __getattr__(name: str) -> object:  # type: ignore[override]
    if name in _EXPORTS:
        module = import_module(_EXPORTS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_EXPORTS.keys()))

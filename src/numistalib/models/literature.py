"""Numista literature models.

Pydantic models for Numista numismatic literature catalogue.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class Publication(NumistaBaseModel):
    """Bibliographic publication record.

    Represents a volume (book), article (authored book chapter),
    series of books (volume_group), or series of articles (article_group).

    Parameters
    ----------
    numista_id : int
        Numista publication ID
    publication_type : str
        Type: volume, article, volume_group, or article_group
    title : str
        Publication title (max 500 chars)
    authors : list[str] | None
        List of author names (optional)
    year : int | None
        Publication year (optional)
    publisher : str | None
        Publisher name (optional, max 255 chars)
    isbn : str | None
        ISBN identifier (optional, max 20 chars)
    pages : str | None
        Page range or count (optional, max 50 chars)
    url : str | None
        External URL reference (optional)

    Examples
    --------
    >>> pub = Publication(
    ...     numista_id=456,
    ...     publication_type="volume",
    ...     title="Standard Catalog of World Coins",
    ...     authors=["George S. Cuhaj"],
    ...     year=2024,
    ...     publisher="Krause Publications",
    ...     isbn="978-1234567890"
    ... )
    >>> print(f"{pub.title} ({pub.year})")
    Standard Catalog of World Coins (2024)
    """

    numista_id: int = Field(description="Numista publication ID")
    publication_type: str = Field(
        max_length=50,
        description="Type: volume, article, volume_group, article_group",
    )
    title: str = Field(max_length=500, description="Publication title")
    authors: list[str] | None = Field(None, description="List of author names")
    year: int | None = Field(None, description="Publication year")
    publisher: str | None = Field(None, max_length=255, description="Publisher name")
    isbn: str | None = Field(None, max_length=20, description="ISBN identifier")
    pages: str | None = Field(None, max_length=50, description="Page range or count")
    url: str | None = Field(None, description="External URL reference")

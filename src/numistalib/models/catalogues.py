"""Numista catalogues models.

Pydantic models for Numista reference catalogues.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class Catalogue(NumistaBaseModel):
    """Reference catalogue information.

    Maps to Numista catalogue entity (e.g., KM, Krause).
    """

    numista_id: int = Field(description="Numista catalogue ID")
    code: str = Field(max_length=50, description="Catalogue code (e.g., KM, Sp)")
    title: str = Field(max_length=1000, description="Catalogue title")
    author: str | None = Field(None, max_length=500, description="Catalogue author")
    publisher: str | None = Field(None, max_length=500, description="Catalogue publisher")
    isbn13: str | None = Field(None, description="ISBN-13")

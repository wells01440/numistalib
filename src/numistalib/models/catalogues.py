"""Numista catalogues models.

Pydantic models for Numista reference catalogues.
"""


from pydantic import Field, computed_field

from numistalib.models.base import NumistaBaseModel


class Catalogue(NumistaBaseModel):
    """Reference catalogue information.

    Maps to Numista catalogue entity (e.g., KM, Krause).
    """

    numista_id: int = Field(alias="id", gt=0, description="Numista catalogue ID")
    code: str = Field(max_length=50, description="Catalogue code (e.g., KM, Sp)")
    title: str = Field(max_length=1000, description="Catalogue title")
    author: str | None = Field(None, max_length=500, description="Catalogue author")
    publisher: str | None = Field(None, max_length=500, description="Catalogue publisher")
    isbn13: str | None = Field(None, description="ISBN-13")

    @computed_field(description="Display label for catalogue")
    def display_label(self) -> str:
        """Formatted label with code and title."""
        return f"{self.code}: {self.title}"

"""Numista issuer import model.

Minimal Pydantic model for importing issuers from Numista API listings.
Aligns with the subset of fields required for the coinlib issuer table
(country_code, name_en, code, numista_id).
"""
import pycountry

from typing import Self, Any

from numistalib.models import Country
from pydantic import Field, computed_field

from rich.repr import Result
from rich.table import Table

from numistalib.models.base import NumistaBaseModel


class Issuer(Country):
    """Issuing country or territory record from Numista.

    Represents a country, territory, or entity that issues coins,
    banknotes, or exonumia. Supports recurse, hierarchical 
    relationships.

    Parameters
    ----------
    code : str
        Slug/short code (primary key, max 100 chars)
    name : str
        Display name (max 255 chars)
    flag : str
        URL to flag image
    wikidata_id : str | None
        Optional Wikidata identifier for cross-reference
    level : int
        Hierarchy level (1=country, 2+=subdivision)
    parent_code : str | None
        Parent issuer code if nested (optional)
    parent_name : str | None
        Parent issuer name if nested (optional)
    raw : dict
        Original API payload

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> issuer = Issuer(
    ...     code="split_notgeld",
    ...     name="Split, City of",
    ...     flag="https://en.numista.com/design/pays/yugoslavia_notgeld.gif",
    ...     wikidata_id="Q1663",
    ...     level=3,
    ...     parent_code="yugoslavia_notgeld",
    ...     parent_name="Yugoslavia Notgeld",
    ...     raw={}
    ... )
    >>> print(f"{issuer.name} (level {issuer.level})")
    Split, City of (level 3)
    """

    # code: str = Field(max_length=100,) # from Country
    # name: str = Field(max_length=255)
    flag: str | None = Field(None, description="Flag URL")
    wikidata_id: str | None = Field(None, description="Wikidata ID")
    level: int | None = Field(None, ge=1, description="Hierarchy (1=country, 2+=subdivision)")
    parent_code: str | None = Field(None, max_length=100, description="Parent code")
    parent_name: str | None = Field(None, max_length=255, description="Parent")

    @computed_field(description="Wikidata URL")
    def wikidata_url(self) -> str | None:
        """Return the Wikidata URL for this issuer, if available."""
        if self.wikidata_id:
            return f"https://www.wikidata.org/wiki/{self.wikidata_id}"


    def render_panel(
            self, 
            title: str = "",
            column_set: str | None = None
        ) -> Any:
        return super().render_panel(title, column_set=column_set)
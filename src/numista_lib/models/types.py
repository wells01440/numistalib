"""Numista catalogue type models.

Pydantic models for Numista coin/banknote/exonumia types.
Used for validation and data transfer between integration and service layers.
"""

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class TypeBasic(NumistaBaseModel):
    """Basic type information from search results.

    Maps to NumistaTypeBasic from API responses.

    Parameters
    ----------
    numista_id : int
        Numista type ID (unique identifier)
    title : str
        Type title (max 500 chars)
    category : str
        Category: coin, banknote, or exonumia
    issuer_code : str
        Issuer code (slug identifier)
    issuer_name : str
        Issuer display name
    min_year : int | None
        First year of production (optional)
    max_year : int | None
        Last year of production (optional)
    obverse_thumbnail : str | None
        Obverse thumbnail URL (optional)
    reverse_thumbnail : str | None
        Reverse thumbnail URL (optional)
    raw : dict
        Original API payload

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> type_basic = TypeBasic(
    ...     numista_id=95420,
    ...     title="1 Thaler",
    ...     category="coin",
    ...     issuer_code="muhlhausen",
    ...     issuer_name="Mühlhausen",
    ...     min_year=1622,
    ...     max_year=1622,
    ...     raw={}
    ... )
    >>> print(type_basic.title)
    1 Thaler
    """

    numista_id: int = Field(description="Numista type ID")
    title: str = Field(max_length=500, description="Type title")
    category: str = Field(max_length=50, description="Category: coin, banknote, exonumia")
    issuer_code: str = Field(max_length=100, description="Issuer code")
    issuer_name: str = Field(max_length=255, description="Issuer name")
    min_year: int | None = Field(None, description="First year of production")
    max_year: int | None = Field(None, description="Last year of production")
    obverse_thumbnail: str | None = Field(None, description="Obverse thumbnail URL")
    reverse_thumbnail: str | None = Field(None, description="Reverse thumbnail URL")

    def to_dict(self) -> dict[str, object]:
        """Convert type to dictionary representation."""
        return self.model_dump(exclude_none=True)


class TypeFull(TypeBasic):
    """Full type details including physical specifications.

    Extends TypeBasic with complete metadata from API responses.

    Parameters
    ----------
    value_text : str | None
        Face value as text (e.g., "1 Dollar")
    value_numeric : float | None
        Numeric face value
    currency_name : str | None
        Currency name
    composition : str | None
        Metal composition (max 500 chars)
    weight : float | None
        Weight in grams
    diameter : float | None
        Diameter in millimeters
    thickness : float | None
        Thickness in millimeters
    obverse_description : str | None
        Obverse description text
    obverse_lettering : str | None
        Obverse lettering/inscription
    reverse_description : str | None
        Reverse description text
    reverse_lettering : str | None
        Reverse lettering/inscription

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> type_full = TypeFull(
    ...     numista_id=95420,
    ...     title="1 Thaler",
    ...     category="coin",
    ...     issuer_code="muhlhausen",
    ...     issuer_name="Mühlhausen",
    ...     composition="Silver",
    ...     weight=28.8,
    ...     diameter=42.0,
    ...     raw={}
    ... )
    >>> print(f"{type_full.weight}g {type_full.composition}")
    28.8g Silver
    """

    value_text: str | None = Field(None, max_length=100, description="Face value text")
    value_numeric: float | None = Field(None, description="Numeric face value")
    currency_name: str | None = Field(None, max_length=100, description="Currency name")
    composition: str | None = Field(None, max_length=500, description="Metal composition")
    weight: float | None = Field(None, description="Weight in grams")
    diameter: float | None = Field(None, description="Diameter in mm")
    thickness: float | None = Field(None, description="Thickness in mm")
    obverse_description: str | None = Field(None, description="Obverse description")
    obverse_lettering: str | None = Field(None, description="Obverse lettering")
    reverse_description: str | None = Field(None, description="Reverse description")
    reverse_lettering: str | None = Field(None, description="Reverse lettering")

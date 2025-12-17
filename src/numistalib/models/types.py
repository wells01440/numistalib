"""Numista catalogue type models.

Pydantic models for Numista coin/banknote/exonumia types.
Used for validation and data transfer between integration and service layers.
"""

from typing import Any

from pydantic import ConfigDict, Field, model_validator, computed_field
from pydantic_core import Url

from numistalib.models import Currency, Issuer, Mint, NumistaBaseModel, Reference


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

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    numista_id: int = Field(alias="id", description="Numista type ID")
    title: str = Field(max_length=500, description="Type title")
    category: str = Field(max_length=50, description="Category: coin, banknote, exonumia")
    issuer_code: str = Field(max_length=100, description="Issuer code")
    issuer_name: str = Field(max_length=255, description="Issuer name")
    min_year: int | None = Field(None, description="First year of production")
    max_year: int | None = Field(None, description="Last year of production")
    obverse_thumbnail: str | None = Field(None, description="Obverse thumbnail URL")
    reverse_thumbnail: str | None = Field(None, description="Reverse thumbnail URL")

    @model_validator(mode="before")
    @classmethod
    def flatten_issuer(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested issuer dict to issuer_code and issuer_name."""
        if "issuer" in data:
            data["issuer_code"] = data["issuer"].get("code")
            data["issuer_name"] = data["issuer"].get("name")
        return data


class CurrencyValue(NumistaBaseModel):
    """Currency value information.

    Maps to Numista currency value entity referenced in type details.

    Parameters
    ----------
    text : str
        Textual representation of the value
    numeric_value : float | None
        Numeric value (optional)
    currency : Currency | None
        Currency information (optional)

    Examples
    --------
    >>> value = CurrencyValue(
    ...     text="1 Thaler",
    ...     numeric_value=1,
    ...     currency=Currency(
    ...         numista_id=6357,
    ...         code="THL",
    ...         full_name="Thaler"
    ...     )
    ... )
    >>> print(value.text)
    1 Thaler
    """

    text: str = Field(description="Textual representation of the value")
    numeric_value: float | None = Field(None, description="Numeric value")
    currency: Currency | None = Field(None, description="Currency information")


class Demonetization(NumistaBaseModel):
    is_demonetized: bool = Field(description="Indicates if the type is demonetized")


class Composition(NumistaBaseModel):
    text: str = Field(description="Metal composition description")


class Technique(NumistaBaseModel):
    text: str = Field(description="Minting technique description")


class LetteringScript(NumistaBaseModel):
    name: str = Field(description="Name of the lettering script")


class References(NumistaBaseModel):
    references: list[Reference] = Field(description="List of references")


class RulerGroup(NumistaBaseModel):
    """Ruler group details.

    Maps to Numista ruler group schema for detailed group information.

    Parameters
    ----------
    id : int
        Unique identifier for the ruler group
    name : str
        Name of the ruler group

    Examples
    --------
    >>> group = RulerGroup(
    ...     id=867,
    ...     name="Emperors of the Holy Roman Empire"
    ... )
    >>> print(group.name)
    Emperors of the Holy Roman Empire
    """

    id: int = Field(..., description="Unique identifier for the ruler group")
    name: str = Field(..., description="Name of the ruler group")


class Ruler(NumistaBaseModel):
    """Ruler details.

    Maps to Numista ruler schema for detailed ruler information.

    Parameters
    ----------
    id : int
        Unique identifier for the ruler
    name : str
        Name of the ruler
    wikidata_id : str | None
        Wikidata identifier (optional)
    group : dict[str, object] | None
        Group information (optional)

    Examples
    --------
    >>> ruler = Ruler(
    ...     id=8536,
    ...     name="Joseph II",
    ...     wikidata_id="Q76555",
    ...     group={"id": 867, "name": "Emperors of the Holy Roman Empire"}
    ... )
    >>> print(ruler.name)
    Joseph II
    """

    id: int = Field(..., description="Unique identifier for the ruler")
    name: str = Field(..., description="Name of the ruler")
    wikidata_id: str | None = Field(None, description="Wikidata identifier")
    group: RulerGroup | None = Field(None, description="Group information")
    
    @computed_field
    def wikidata_url(self) -> Url | None:
        """Computed Wikidata URL from `wikidata_id`.

        Returns
        -------
        Url | None
            Full Wikidata URL if `wikidata_id` present, else None.
        """
        if self.wikidata_id:
            return Url(f"https://www.wikidata.org/wiki/{self.wikidata_id}")
        return None
    


class Obverse(NumistaBaseModel):
    description: str = Field(description="Obverse description")
    lettering: str = Field(description="Obverse lettering/inscription")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Obverse lettering scripts")
    picture: Url = Field(description="Obverse picture URL")
    thumbnail: Url = Field(description="Obverse thumbnail URL")
    picture_copyright: str = Field(description="Obverse picture copyright")
    picture_copyright_url: Url = Field(description="Obverse picture copyright URL")
    lettering_translation: str | None = Field(None, description="Translation of obverse lettering/inscription")



class Reverse(NumistaBaseModel):
    description: str = Field(description="Reverse description")
    lettering: str = Field(description="Reverse lettering/inscription")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Reverse lettering scripts")
    picture: Url = Field(description="Reverse picture URL")
    thumbnail: Url = Field(description="Reverse thumbnail URL")
    picture_copyright: str = Field(description="Reverse picture copyright")
    picture_copyright_url: Url = Field(description="Reverse picture copyright URL")


class TypeFull(NumistaBaseModel):
    """Full type details including physical specifications."""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(description="Numista type ID")
    url: Url = Field(description="Numista type URL")
    title: str = Field(max_length=500, description="Type title", )
    category: str = Field(max_length=50, description="Category: coin, banknote, exonumia")
    issuer: Issuer = Field(description="Issuer information")
    min_year: int | None = Field(None, description="First year of production")
    max_year: int | None = Field(None, description="Last year of production")
    type: str | None = Field(None, max_length=100, description="Type classification")
    rulers: list[Ruler] | None = Field(None, alias="ruler", description="Ruler information")
    value: CurrencyValue | None = Field(None, description="Currency value information")
    demonetization: Demonetization | None = Field(None, description="Demonetization information")
    size: float | None = Field(None, description="Size in millimeters")
    shape: str | None = Field(None, max_length=100, description="Shape description")
    composition: Composition | None = Field(None, description="Metal composition information")
    technique: Technique | None = Field(None, description="Minting technique information")
    obverse: Obverse | None = Field(None, description="Obverse details")
    reverse: Reverse | None = Field(None, description="Reverse details")
    references: list[Reference] | None = Field(None, description="List of references")
    mints: list[Mint] | None = Field(None, description="List of mints")
    comments: str | None = Field(None, description="Additional comments")
    tags: list[str] | None = Field(None, description="List of tags")
    weight: float | None = Field(None, description="Weight in grams")
    edge: dict[str, Any] | None = Field(None, description="Edge description")



    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        """Preprocess API data to normalize nested structures."""
        if not isinstance(data, dict):
            return data

        # Normalize references catalogue field from dict to string
        if "references" in data and isinstance(data["references"], list):
            for ref in data["references"]:
                if isinstance(ref, dict) and "catalogue" in ref:
                    cat = ref["catalogue"]
                    if isinstance(cat, dict) and "code" in cat:
                        ref["catalogue"] = cat["code"]

        return data

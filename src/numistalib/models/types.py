"""Numista catalogue type models.

Pydantic models for Numista coin/banknote/exonumia types.
Used for validation and data transfer between integration and service layers.
"""

from abc import ABC
from typing import Any, Annotated, Literal

from pydantic import (
    Field,
    HttpUrl,
    AnyUrl,
    StringConstraints,
    computed_field,
    model_validator,
)
from pydantic_core import Url
from numistalib.models import Currency, Issuer, Mint, NumistaBaseModel, Reference

class Country(NumistaBaseModel):
    code: str = Field(max_length=10)
    name: str = Field(max_length=255)

class CurrencyValue(NumistaBaseModel):
    """Currency value information."""

    text: str = Field(description="Textual representation of the value")
    numeric_value: float | None = Field(None, description="Numeric value")
    numerator: int | None = Field(None, description="Numerator for fractional values")
    denominator: int | None = Field(None, description="Denominator for fractional values")
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
  
    id: int = Field(..., description="Unique identifier for the ruler group")
    name: str = Field(..., description="Name of the ruler group")


class Ruler(NumistaBaseModel):
    """Maps to Numista ruler schema for detailed ruler information."""

    id: int = Field(..., description="Unique identifier for the ruler")
    name: str = Field(..., description="Name of the ruler")
    wikidata_id: str | None = Field(None, description="Wikidata identifier")
    nomisma_id: str | None = Field(None, description="Nomisma identifier")
    group: RulerGroup | None = Field(None, description="Group information")
    
    @property
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
    engravers: list[str] | None = Field(None, description="List of obverse engravers")
    description: str = Field(description="Obverse description")
    lettering: str = Field(description="Obverse lettering/inscription")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Obverse lettering scripts")
    picture: AnyUrl = Field(description="Obverse picture URL")
    thumbnail: AnyUrl = Field(description="Obverse thumbnail URL")
    picture_copyright: str = Field(description="Obverse picture copyright")
    picture_copyright_url: AnyUrl = Field(description="Obverse picture copyright URL")
    lettering_translation: str | None = Field(None, description="Translation of obverse lettering/inscription")



class Reverse(NumistaBaseModel):
    engravers: list[str] | None = Field(None, description="List of reverse engravers")
    description: str = Field(description="Reverse description")
    lettering: str = Field(description="Reverse lettering/inscription")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Reverse lettering scripts")
    picture: AnyUrl = Field(description="Reverse picture URL")
    thumbnail: AnyUrl = Field(description="Reverse thumbnail URL")
    picture_copyright: str = Field(description="Reverse picture copyright")
    picture_copyright_url: AnyUrl = Field(description="Reverse picture copyright URL")
    lettering_translation: str | None = Field(None, description="Translation of reverse lettering/inscription")

class TypeBase(NumistaBaseModel, ABC):
    """Common fields shared between basic and full type representations."""
    
    numista_id: int = Field(alias="id", gt=0, description="Numista type ID")
    title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] = Field(
        ..., description="Type title"
    )
    
    category: Literal["coin", "banknote", "exonumia"] = Field(
        ..., description="Category: coin, banknote, exonumia"
    )
    min_year: int | None = Field(None, ge=-9999, le=9999, description="First year of production")  # Allow BC dates
    max_year: int | None = Field(None, ge=-9999, le=9999, description="Last year of production")
    
    @computed_field(description="Human-readable year range")
    @property
    def year_range(self) -> str:
        if self.min_year and self.max_year:
            if self.min_year == self.max_year:
                return str(self.min_year)
            return f"{self.min_year}–{self.max_year}"
        elif self.min_year:
            return f"{self.min_year}–"
        elif self.max_year:
            return f"–{self.max_year}"
        return "Undated"
    @computed_field(description="Canonical Numista page URL")
    @property
    def numista_url(self) -> HttpUrl:
        return HttpUrl(f"https://en.numista.com/{self.numista_id}")
    
    @model_validator(mode="after")
    def validate_years(self) -> "TypeBase":
        if self.min_year is not None and self.max_year is not None:
            if self.min_year > self.max_year:
                raise ValueError("min_year cannot be greater than max_year")
        return self

class TypeBasic(TypeBase):
    """Basic type information from search results."""
    
    country: Country | None = Field(None, description="Country information")
    min_year: int | None = Field(None, ge=0, le=9999, description="First year of production")
    max_year: int | None = Field(None, ge=0, le=9999, description="Last year of production")
    obverse_thumbnail: HttpUrl | None = Field(None, description="Obverse thumbnail URL")
    reverse_thumbnail: HttpUrl | None = Field(None, description="Reverse thumbnail URL")


class TypeFull(TypeBase):
    """Full type details including physical specifications."""
    # Required fields that only exist in full version
    url: HttpUrl = Field(..., description="Numista type URL")
    issuer: Issuer = Field(..., description="Issuer information")
    # Optional full-only fields
    type: str | None = Field(None, max_length=100, description="Type classification")
    rulers: list[Ruler] | None = Field(None, alias="ruler")
    value: CurrencyValue | None = Field(None)
    demonetization: Demonetization | None = Field(None)
    size: float | None = Field(None, ge=0)
    thickness: float | None = Field(None, ge=0)
    weight: float | None = Field(None, ge=0)
    shape: str | None = Field(None, max_length=100)
    composition: Composition | None = Field(None)
    technique: Technique | None = Field(None)
    obverse: Obverse | None = Field(None)
    reverse: Reverse | None = Field(None)
    references: list[Reference] | None = Field(None)
    mints: list[Mint] | None = Field(None)
    comments: str | None = Field(None)
    tags: list[str] | None = Field(None)
    edge: dict[str, Any] | None = Field(None)
    related_types: list[TypeBasic] | None = Field(None)  # Note: recursive, but TypeBasic is defined
    orientation: str | None = Field(None)

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

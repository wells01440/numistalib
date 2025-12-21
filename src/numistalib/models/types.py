"""Numista catalogue type models.

Pydantic models for Numista coin/banknote/exonumia types.
Used for validation and data transfer between integration and service layers.
"""

from __future__ import annotations

from abc import ABC
from datetime import date
from functools import cached_property
from io import BytesIO
from typing import Annotated, Any, Literal

import httpx
from PIL import Image as PILImage
from pydantic import (
    AnyUrl,
    Field,
    HttpUrl,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_core import Url
from textual_image.renderable import Image as TImage


from numistalib.models import Currency, Issuer, Mint, NumistaBaseModel, Reference
from numistalib.models.issues import IssueTerms

class Country(NumistaBaseModel):
    code: str = Field(max_length=50)
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
    demonetization_date: date | None = Field(None, description="Date of demonetization")


    @field_validator("demonetization_date", mode="before")
    @classmethod
    def parse_partial_date(cls, v: Any) -> date | None:
        """Handle partial dates with 00 day or month and various formats."""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Skip partial dates with 00
            if "00" in v or v.endswith("-00"):
                return None
            # Try multiple date formats
            from datetime import datetime
            formats = [
                "%Y-%m-%d",      # 1988-02-15
                "%Y/%m/%d",      # 1988/02/15
                "%d-%m-%Y",      # 15-02-1988
                "%d/%m/%Y",      # 15/02/1988
                "%m-%d-%Y",      # 02-15-1988
                "%m/%d/%Y",      # 02/15/1988
                "%Y",            # 1988 (year only)
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            return None
        return None


class Composition(NumistaBaseModel):
    text: str = Field(description="Metal composition description")


class Technique(NumistaBaseModel):
    text: str = Field(description="Minting technique description")


class LetteringScript(NumistaBaseModel):
    name: str = Field(description="Name of the lettering script")


class References(NumistaBaseModel):
    references: list[Reference] = Field(description="List of references")

   
class RulerGroup(NumistaBaseModel):

    id: int = Field(..., description="Numista ID", alias="numista_id")
    name: str = Field(..., description="Group Name")



class Ruler(NumistaBaseModel):
    """Maps to Numista ruler schema for detailed ruler information."""

    id: int = Field(..., description="Numista ID", alias="numista_id")
    name: str = Field(..., description="Ruler Name")
    wikidata_id: str | None = Field(None, description="Wikidata ID")
    nomisma_id: str | None = Field(None, description="Nomisma ID")
    group: RulerGroup | None = Field(None, description="Group information")

    @computed_field
    @property
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
    

class SideBase(NumistaBaseModel, ABC):
    """Base class for obverse and reverse sides of a type."""
    engravers: list[str] | None = Field(None, description="List of engravers")
    designers: list[str] | None = Field(None, description="List of designers")
    description: str = Field(description="Description of the side")
    lettering: str | None = Field(None, description="Lettering/inscription on the side")
    lettering_scripts: list[LetteringScript] | None = Field(None, description="Lettering scripts used")
    picture: AnyUrl = Field(description="Picture URL of the side")
    thumbnail: AnyUrl = Field(description="Thumbnail URL of the side")
    picture_copyright: str | None = Field(None, description="Picture copyright information")
    picture_copyright_url: AnyUrl | None = Field(None, description="URL for picture copyright information")
    picture_license_name: str | None = Field(None, description="Picture license name")
    picture_license_url: AnyUrl | None = Field(None, description="Picture license URL")
    lettering_translation: str | None = Field(None, description="Translation of the lettering/inscription")
    unabridged_legend: str | None = Field(None, description="Full unabridged lettering")

    @computed_field(description="Cleaned lettering as lines")
    def lettering_lines(self) -> list[str]:
        """Splits the lettering into individual lines using the embedded line break."""
        if not self.lettering:
            return []
        return [line.strip() for line in self.lettering.splitlines() if line.strip()]

    @cached_property
    def pillow_image(self) -> PILImage.Image:
        """Download and cache the full picture as a Pillow Image."""
        response = httpx.get(self.picture.encoded_string(), follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return PILImage.open(BytesIO(response.content))

    @cached_property
    def pillow_thumbnail(self) -> PILImage.Image:
        """Download and cache the thumbnail as a Pillow Image."""
        response = httpx.get(self.thumbnail.encoded_string(), follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        return PILImage.open(BytesIO(response.content))

    @cached_property
    def renderable_image(self) -> Any | None:
        """Ready-to-print textual_image renderable (full picture)."""
        try:
            img = TImage(self.pillow_image)
            return img
        except ImportError:
            return None

    @cached_property
    def renderable_thumbnail(self) -> Any | None:
        """Ready-to-print thumbnail."""
        try:
            img = TImage(self.pillow_thumbnail)
            return img
        except ImportError:
            return None

    @computed_field(description="Formatted copyright link for textual display")
    def copyright_link(self) -> str:
        """Formatted copyright link for textual display."""
        return f"[link={self.picture_copyright_url}]{self.picture_copyright}[/link]"

    @computed_field(description="Formatted thumbnail link for textual display")
    def thumbnail_link(self) -> str:
        """Formatted thumbnail link for textual display."""
        return f"[link={self.thumbnail}]{self.thumbnail}[/link]"

    @computed_field(description="Formatted picture link for textual display")
    def picture_link(self) -> str:
        """Formatted picture link for textual display."""
        return f"[link={self.picture}]{self.picture}[/link]"


class Obverse(SideBase):
    pass


class Reverse(SideBase):
    pass


class TypeBase(NumistaBaseModel, ABC):
    """Common fields shared between basic and full type representations."""
    numista_id: int = Field(alias="id", gt=0, description="Numista ID")
    title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] = Field(
        ..., description="Type title"
    )

    category: Literal["coin", "banknote", "exonumia"] = Field(
        ..., description="Category: coin, banknote, exonumia"
    )
    min_year: int | None = Field(None, ge=-9999, le=9999, description="First year of production")  # Allow BC dates
    max_year: int | None = Field(None, ge=-9999, le=9999, description="Last year of production")

    @computed_field(description="Human-readable year range")
    def year_range(self) -> str:
        if self.min_year and self.max_year:
            if self.min_year == self.max_year:
                return str(self.min_year)
            return f"{self.min_year}-{self.max_year}"
        elif self.min_year:
            return f"{self.min_year}-"
        elif self.max_year:
            return f"-{self.max_year}"
        return "Undated"

    @computed_field(description="Canonical Numista page URL")
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

    # Required fields that only exist in full version
    url: HttpUrl = Field(..., description="Numista type URL")
    issuer: Issuer = Field(..., description="Issuer information")
    # Optional full-only fields
    issue_terms: IssueTerms | None = Field(None, alias="issueTerms", description="Issue Terms")
    issuing_entity: dict[str, Any] | None = Field(None, description="Issuing entity information")
    secondary_issuing_entity: dict[str, Any] | None = Field(None, description="Secondary Issuing entity information")
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
    series: str | None = Field(None, description="Series or set designation")
    commemorated_topic: str | None = Field(None, description="Topic being commemorated")

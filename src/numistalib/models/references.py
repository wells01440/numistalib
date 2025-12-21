"""Numista reference and localized label models.

Pydantic models for reference catalogues and multilingual labels.
"""


from pydantic import Field, HttpUrl, computed_field

from numistalib.models.base import NumistaBaseModel


class Reference(NumistaBaseModel):
    """Reference catalogue information."""
    catalogue: str = Field(max_length=50, description="Catalogue code")
    number: str = Field(max_length=100, description="Catalogue reference number")
    url: HttpUrl | None = Field(None, description="External URL to reference")

    @computed_field(description="Formatted reference display")
    def display_reference(self) -> str:
        """Formatted catalogue reference."""
        return f"{self.catalogue} {self.number}"


class LocalizedLabel(NumistaBaseModel):
    """Localized text label.

    Maps to Numista localized_label schema for multilingual content.

    Parameters
    ----------
    language : str
        ISO 639-1 language code (2 chars)
    label : str
        Localized text content (max 500 chars)

    Examples
    --------
    >>> label_en = LocalizedLabel(language="en", label="United States")
    >>> label_es = LocalizedLabel(language="es", label="Estados Unidos")
    >>> print(f"{label_en.language}: {label_en.label}")
    en: United States
    """

    language: str = Field(max_length=2, description="ISO 639-1 language code")
    label: str = Field(max_length=500, description="Localized text content")

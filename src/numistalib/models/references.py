"""Numista reference and localized label models.

Pydantic models for reference catalogues and multilingual labels.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class Reference(NumistaBaseModel):
    """Reference catalogue cross-reference.

    Maps to Numista reference schema for catalogue numbers
    (e.g., KM#123, Sp#456).

    Parameters
    ----------
    catalogue : str
        Catalogue code (max 50 chars)
    number : str
        Catalogue number (max 100 chars)
    url : str | None
        External URL to reference (optional)

    Examples
    --------
    >>> ref = Reference(
    ...     catalogue="KM",
    ...     number="123.1",
    ...     url="https://example.com/km-123-1"
    ... )
    >>> print(f"{ref.catalogue}#{ref.number}")
    KM#123.1
    """

    catalogue: str = Field(max_length=50, description="Catalogue code")
    number: str = Field(max_length=100, description="Catalogue number")
    url: str | None = Field(None, description="External URL to reference")

    def to_dict(self) -> dict[str, object]:
        """Convert reference to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation of the reference
        """
        return self.model_dump(exclude_none=True)


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


__all__ = [
    "LocalizedLabel",
    "Reference",
]

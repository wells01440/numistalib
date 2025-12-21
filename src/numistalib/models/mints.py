"""Numista mints models.

Pydantic models for Numista mint facilities.
"""

from pydantic import Field, computed_field

from numistalib.models.base import NumistaBaseModel


class Mint(NumistaBaseModel):
    """Mint facility information.

    Maps to Numista mint entity.
    """

    id: int = Field(alias="numista_id", gt=0, description="Numista ID")
    name: str = Field(max_length=255, description="Mint facility name")
    code: str | None = Field(None, max_length=50, description="Mint code or abbreviation")
    country_code: str | None = Field(None, max_length=50, description="Issuing country code")

    @computed_field(description="Formatted mint identifier")
    def mint_identifier(self) -> str:
        """Mint code if available, otherwise name."""
        return self.code if self.code else self.name

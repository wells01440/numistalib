"""Numista mints models.

Pydantic models for Numista mint facilities.
"""

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class Mint(NumistaBaseModel):
    """Mint facility information.

    Maps to Numista mint entity.
    """

    numista_id: int = Field(description="Numista mint ID")
    name: str = Field(max_length=255, description="Mint name")
    code: str | None = Field(None, max_length=50, description="Mint code")
    country_code: str | None = Field(None, max_length=50, description="Country code")

    def to_dict(self) -> dict[str, object]:
        """Convert mint to dictionary representation."""
        return self.model_dump(exclude_none=True)

"""Numista mints models.

Pydantic models for Numista mint facilities.
"""

from pydantic import ConfigDict, Field

from numistalib.models.base import NumistaBaseModel


class Mint(NumistaBaseModel):
    """Mint facility information.

    Maps to Numista mint entity.
    """

    model_config = ConfigDict(populate_by_name=True)

    numista_id: int = Field(alias="id", description="Numista mint ID")
    name: str = Field(max_length=255, description="Mint name")
    code: str | None = Field(None, max_length=50, description="Mint code")
    country_code: str | None = Field(None, max_length=50, description="Country code")

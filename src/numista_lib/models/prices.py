"""Numista prices models.

Pydantic models for Numista price estimates.
"""

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class Price(NumistaBaseModel):
    """Price estimate for a specific issue and grade.

    Maps to Numista price data.
    """

    issue_id: int = Field(description="Issue ID")
    grade: str = Field(max_length=10, description="Grade (g, vg, f, vf, xf, au, unc)")
    currency: str = Field(max_length=3, description="ISO 4217 currency code")
    value: float = Field(description="Price estimate")

    def to_dict(self) -> dict[str, object]:
        """Convert price to dictionary representation."""
        return self.model_dump()

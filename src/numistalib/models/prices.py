"""Numista prices models.

Pydantic models for Numista price estimates.
"""


from pydantic import Field, computed_field

from numistalib.models.base import NumistaBaseModel


class Price(NumistaBaseModel):
    """Price estimate for a specific issue and grade.

    Maps to Numista price data.
    """

    issue_id: int = Field(gt=0, description="Issue ID")
    grade: str = Field(max_length=10, description="Grade (g, vg, f, vf, xf, au, unc)")
    currency: str = Field(max_length=3, description="ISO 4217 currency code")
    value: float = Field(ge=0, description="Price estimate")

    @computed_field(description="Formatted price display")
    def formatted_price(self) -> str:
        """Price with currency code."""
        return f"{self.currency} {self.value:.2f}"

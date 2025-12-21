"""Numista collections models.

Pydantic models for Numista user collections.
"""

from datetime import date as date_type

from pydantic import Field, computed_field

from numistalib.models.base import NumistaBaseModel


class UserCollection(NumistaBaseModel):
    """User-defined collection container.

    Represents a named collection that groups collected items for a user.
    """

    numista_id: int = Field(alias="id", gt=0, description="Numista collection ID")
    user_id: int = Field(gt=0, description="Owner user ID")
    name: str = Field(max_length=255, description="Collection name")

    @computed_field(description="Collection description")
    def collection_label(self) -> str:
        """Label combining user and collection name."""
        return f"{self.name} (User {self.user_id})"

    def to_dict(self) -> dict[str, object]:
        """Convert collection to dictionary representation."""
        return self.model_dump()


class CollectedItem(NumistaBaseModel):
    """Item in a user's collection.

    Maps to Numista collected_item entity.
    """

    numista_id: int = Field(alias="id", gt=0, description="Numista collected item ID")
    user_id: int = Field(gt=0, description="Owner user ID")
    type_id: int = Field(gt=0, description="Type ID")
    issue_id: int | None = Field(None, gt=0, description="Specific issue ID")
    quantity: int = Field(default=1, ge=0, description="Quantity owned")
    grade: str | None = Field(None, max_length=10, description="Grade (g, vg, f, vf, xf, au, unc)")
    for_swap: bool = Field(default=False, description="Available for swap")
    price_value: float | None = Field(None, ge=0, description="Purchase price")
    price_currency: str | None = Field(None, max_length=3, description="Price currency code")
    acquisition_date: date_type | None = Field(None, description="Date acquired")
    storage_location: str | None = Field(None, max_length=255, description="Storage location")

    @computed_field(description="Item summary for display")
    def item_summary(self) -> str:
        """Summary of collected item."""
        parts = [f"Type {self.type_id}"]
        if self.issue_id:
            parts.append(f"Issue {self.issue_id}")
        if self.quantity > 1:
            parts.append(f"x{self.quantity}")
        if self.grade:
            parts.append(f"({self.grade})")
        return " ".join(parts)

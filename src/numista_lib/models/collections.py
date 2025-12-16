"""Numista collections models.

Pydantic models for Numista user collections.
"""

from datetime import date as date_type

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class UserCollection(NumistaBaseModel):
    """User-defined collection container.

    Represents a named collection that groups collected items for a user.
    """

    numista_id: int = Field(description="Numista collection ID")
    user_id: int = Field(description="Owner user ID")
    name: str = Field(description="Collection name")

    def to_dict(self) -> dict[str, object]:
        """Convert collection to dictionary representation."""
        return self.model_dump()


class CollectedItem(NumistaBaseModel):
    """Item in a user's collection.

    Maps to Numista collected_item entity.
    """

    numista_id: int = Field(description="Numista collected item ID")
    user_id: int = Field(description="Owner user ID")
    type_id: int = Field(description="Type ID")
    issue_id: int | None = Field(None, description="Specific issue ID")
    quantity: int = Field(default=1, description="Quantity owned")
    grade: str | None = Field(None, max_length=10, description="Grade")
    for_swap: bool = Field(default=False, description="Available for swap")
    price_value: float | None = Field(None, description="Purchase price")
    price_currency: str | None = Field(None, max_length=3, description="Price currency")
    acquisition_date: date_type | None = Field(None, description="Date acquired")
    storage_location: str | None = Field(None, max_length=255, description="Storage location")

    def to_dict(self) -> dict[str, object]:
        """Convert collected item to dictionary representation."""
        return self.model_dump(exclude_none=True)

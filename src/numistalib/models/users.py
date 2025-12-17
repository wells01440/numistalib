"""Numista users models.

Pydantic models for Numista user profiles.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class User(NumistaBaseModel):
    """Numista user profile information.

    Maps to Numista user entity.
    """

    numista_id: int = Field(description="Numista user ID")
    username: str = Field(max_length=100, description="Username")
    country_code: str | None = Field(None, max_length=10, description="User country")
    member_since: str | None = Field(None, description="Registration date")

    def to_dict(self) -> dict[str, object]:
        """Convert user to dictionary representation."""
        return self.model_dump(exclude_none=True)

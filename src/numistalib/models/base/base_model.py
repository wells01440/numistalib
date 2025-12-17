"""Base models for all Numista entities.

Provides common configuration, behavior, and abstract base classes for Pydantic models.
"""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class NumistaBaseModel(ABC, BaseModel):
    """Base model for all Numista entities.

    Provides:
    - Strict validation
    - Immutability control
    - Extra field prohibition
    - Consistent configuration
    """

    model_config = ConfigDict(
        strict=True,
        frozen=False,
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=False,
        populate_by_name=True,
    )

    def to_dict(self) -> dict[str, object]:
        """Convert model to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation of the model
        """
        return self.model_dump(exclude_none=True)

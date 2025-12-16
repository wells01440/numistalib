"""Base models for all Numista entities.

Provides common configuration, behavior, and abstract base classes for Pydantic models.
"""

from abc import ABC, abstractmethod

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
    )

    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        """Convert model to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation of the model
        """
        pass

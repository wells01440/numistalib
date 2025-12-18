"""Base models for all Numista entities.

Common configuration, behavior, and abstract base classes for Pydantic models.
"""
import rich.repr

from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NumistaBaseModel(ABC, BaseModel):
    """Base model for all Numista entities.

    Common configuration, behavior, and abstract base classes for Pydantic models.
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
        alias_generator=to_camel,
        use_enum_values=True,
    )

    def __rich_repr__(self) -> rich.repr.Result:
        """Make models look good when printed with rich.print()."""
        for name, field in self.__class__.model_fields.items():
            if field.alias:
                value = getattr(self, name)
                if value is not None:  # Skip None fields for cleaner output
                    yield field.alias or name, value
            else:
                yield name, getattr(self, name)

    def to_api_dict(self, **kwargs: Any) -> dict[Any, Any ]:
        """Return dict suitable for sending back to API or clean export.
        Uses aliases, excludes None by default.
        """
        return self.model_dump(
            by_alias=kwargs.get("by_alias", True),
            exclude_none=kwargs.get("exclude_none", True),
            exclude_unset= kwargs.get("exclude_unset", True),
            **kwargs,
        )

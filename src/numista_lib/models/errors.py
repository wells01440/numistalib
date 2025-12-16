"""Numista error models.

Pydantic models for Numista API error responses.
"""

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class ErrorResponse(NumistaBaseModel):
    """API error response.

    Maps to Numista error schema from API responses.

    Parameters
    ----------
    error_message : str
        Human-readable error description

    Examples
    --------
    >>> error = ErrorResponse(error_message="Invalid API key")
    >>> print(error.error_message)
    Invalid API key
    """

    error_message: str = Field(description="Error description")

    def to_dict(self) -> dict[str, object]:
        """Convert error to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary with error_message key
        """
        return {"error_message": self.error_message}


__all__ = ["ErrorResponse"]

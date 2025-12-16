"""Numista currency models.

Pydantic models for Numista currency information.
"""

from pydantic import Field

from numista_lib.models.base import NumistaBaseModel


class Currency(NumistaBaseModel):
    """Currency information.

    Maps to Numista currency entity referenced in type details.

    Parameters
    ----------
    numista_id : int
        Numista currency ID
    code : str
        ISO 4217 currency code (max 10 chars)
    full_name : str
        Full currency name (max 255 chars)
    symbol : str | None
        Currency symbol (optional)

    Examples
    --------
    >>> currency = Currency(
    ...     numista_id=123,
    ...     code="USD",
    ...     full_name="United States Dollar",
    ...     symbol="$"
    ... )
    >>> print(f"{currency.symbol} {currency.full_name}")
    $ United States Dollar
    """

    numista_id: int = Field(description="Numista currency ID")
    code: str = Field(max_length=10, description="ISO 4217 currency code")
    full_name: str = Field(max_length=255, description="Full currency name")
    symbol: str | None = Field(None, max_length=10, description="Currency symbol")

    def to_dict(self) -> dict[str, object]:
        """Convert currency to dictionary representation.

        Returns
        -------
        dict[str, object]
            Dictionary representation of the currency
        """
        return self.model_dump(exclude_none=True)


__all__ = ["Currency"]

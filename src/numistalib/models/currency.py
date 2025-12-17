"""Numista currency models.

Pydantic models for Numista currency information.
"""

from pydantic import ConfigDict, Field

from numistalib.models.base import NumistaBaseModel


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

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    numista_id: int = Field(alias="id", description="Numista currency ID")
    code: str | None = Field(None, max_length=10, description="ISO 4217 currency code")
    full_name: str = Field(max_length=255, description="Full currency name")
    symbol: str | None = Field(None, max_length=10, description="Currency symbol")

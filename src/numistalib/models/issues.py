"""Numista issues models.

Pydantic models for Numista coin issues (specific years/mints of a type).
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class Issue(NumistaBaseModel):
    """Coin issue (specific year/mint of a type).

    Maps to Numista issue entity. Issues represent specific mintings
    of a type with particular year, mint mark, or variety.

    Parameters
    ----------
    numista_id : int
        Numista issue ID (unique identifier)
    type_id : int
        Parent type ID
    is_dated : bool
        Whether issue has a visible date on the coin
    year : int | None
        Year visible on coin (optional)
    gregorian_year : int | None
        Gregorian calendar year (optional)
    mint_letter : str | None
        Mint mark or letter (max 10 chars, optional)
    mintage : int | None
        Number of coins minted (optional)
    comment : str | None
        Additional notes or variety information (optional)
    raw : dict
        Original API payload

    Raises
    ------
    ValidationError
        If required fields missing or invalid types

    Examples
    --------
    >>> issue = Issue(
    ...     numista_id=123456,
    ...     type_id=95420,
    ...     is_dated=True,
    ...     year=1622,
    ...     gregorian_year=1622,
    ...     mint_letter="D",
    ...     mintage=50000,
    ...     raw={}
    ... )
    >>> print(f"{issue.year} {issue.mint_letter}")
    1622 D
    """

    numista_id: int = Field(description="Numista issue ID")
    type_id: int = Field(description="Parent type ID")
    is_dated: bool = Field(description="Whether issue has a visible date")
    year: int | None = Field(None, description="Year visible on coin")
    gregorian_year: int | None = Field(None, description="Gregorian calendar year")
    mint_letter: str | None = Field(None, max_length=10, description="Mint mark")
    mintage: int | None = Field(None, description="Number minted")
    comment: str | None = Field(None, description="Additional notes")

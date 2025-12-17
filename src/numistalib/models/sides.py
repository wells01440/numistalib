"""Numista coin side models.

Pydantic models for coin obverse and reverse details.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class CoinSide(NumistaBaseModel):
    """Coin side (obverse or reverse) details.

    Maps to Numista coin_side schema for detailed side information.

    Parameters
    ----------
    engravers : list[str] | None
        List of engraver names (optional)
    description : str | None
        Visual description of the side (optional)
    lettering : str | None
        Text inscription on the side (optional)
    thumbnail : str | None
        Thumbnail image URL (optional)
    picture : str | None
        Full-size image URL (optional)

    Examples
    --------
    >>> side = CoinSide(
    ...     engravers=["Augustus Saint-Gaudens"],
    ...     description="Walking Liberty holding torch and olive branch",
    ...     lettering="LIBERTY IN GOD WE TRUST",
    ...     thumbnail="https://example.com/thumb.jpg"
    ... )
    >>> print(side.engravers[0])
    Augustus Saint-Gaudens
    """

    engravers: list[str] | None = Field(None, description="List of engraver names")
    description: str | None = Field(None, description="Visual description")
    lettering: str | None = Field(None, description="Text inscription")
    thumbnail: str | None = Field(None, description="Thumbnail image URL")
    picture: str | None = Field(None, description="Full-size image URL")


__all__ = ["CoinSide"]

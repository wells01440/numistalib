from __future__ import annotations

from typing import TYPE_CHECKING

import pycountry
from pydantic import Field
from pydantic import PrivateAttr
from pydantic import computed_field

from numistalib.models.base import NumistaBaseModel

if TYPE_CHECKING:
    from pycountry.db import Country as PyCountryCountry


class Country(NumistaBaseModel):
    code: str = Field(max_length=50)
    name: str = Field(max_length=255)

    _pycountry_country: PyCountryCountry | None = PrivateAttr(default=None)
    _pycountry_loaded: bool = PrivateAttr(default=False)

    def __str__(self) -> str:
        """Return formatted country with code and name."""
        return f"{self.name} ({self.code})"

    def _get_pycountry_country(self) -> PyCountryCountry | None:
        """Return the matched pycountry Country object (cached, not serialized)."""
        if self._pycountry_loaded:
            return self._pycountry_country

        self._pycountry_loaded = True

        if not self.name:
            self._pycountry_country = None
            return None

        try:
            matches = pycountry.countries.search_fuzzy(self.name)
        except LookupError:
            self._pycountry_country = None
            return None

        self._pycountry_country = matches[0] if matches else None
        return self._pycountry_country

    def _get_pycountry_scalar(self, attr_name: str) -> str | None:
        """Return a scalar string attribute from pycountry, if available."""
        pyc = self._get_pycountry_country()
        if pyc is None:
            return None

        value = getattr(pyc, attr_name, None)
        if isinstance(value, str) and value:
            return value

        return None

    @computed_field(
        return_type=str | None,
        description="ISO 3166-1 alpha-2 code (from pycountry).",
    )
    @property
    def alpha_2(self) -> str | None:
        """Return ISO 3166-1 alpha-2 code derived from pycountry."""
        return self._get_pycountry_scalar("alpha_2")

    @computed_field(
        return_type=str | None,
        description="ISO 3166-1 alpha-3 code (from pycountry).",
    )
    @property
    def alpha_3(self) -> str | None:
        """Return ISO 3166-1 alpha-3 code derived from pycountry."""
        return self._get_pycountry_scalar("alpha_3")

    @computed_field(
        return_type=str | None,
        description="ISO 3166-1 numeric code (from pycountry).",
    )
    @property
    def numeric(self) -> str | None:
        """Return ISO 3166-1 numeric code derived from pycountry."""
        return self._get_pycountry_scalar("numeric")

    @computed_field(
        return_type=str | None,
        description="Flag emoji derived from pycountry, if available.",
    )
    def pyc_flag(self) -> str | None:
        """Return the pycountry-derived flag emoji, if available."""
        pyc = self._get_pycountry_country()
        if pyc is None:
            return None

        flag = getattr(pyc, "flag", None)
        if isinstance(flag, str) and flag:
            return flag

        return None

    @computed_field(
        return_type=str | None,
        description="Canonical country name from pycountry (may differ from API name).",
    )
    @property
    def pyc_name(self) -> str | None:
        """Return canonical country name derived from pycountry."""
        return self._get_pycountry_scalar("name")

    @computed_field(
        return_type=str | None,
        description="Official country name from pycountry, if present.",
    )
    @property
    def pyc_official_name(self) -> str | None:
        """Return official country name derived from pycountry."""
        return self._get_pycountry_scalar("official_name")

    # @computed_field(
    #     return_type=dict[str, str] | None,
    #     description="Convenience dict of pycountry-derived scalar fields.",
    # )
    # @property
    # def country_info(self) -> dict[str, str] | None:
    #     """Return scalar pycountry fields if available, else None."""
    #     alpha_2 = self.alpha_2
    #     alpha_3 = self.alpha_3
    #     numeric = self.numeric
    #     name = self.pyc_name
    #     official_name = self.pyc_official_name

    #     info: dict[str, str] = {}

    #     if alpha_2:
    #         info["alpha_2"] = alpha_2
    #     if alpha_3:
    #         info["alpha_3"] = alpha_3
    #     if numeric:
    #         info["numeric"] = numeric
    #     if name:
    #         info["name"] = name
    #     if official_name:
    #         info["official_name"] = official_name

    #     return info or None
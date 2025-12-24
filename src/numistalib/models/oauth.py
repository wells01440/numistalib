"""OAuth models."""

# Standard library

# Third-party

# Local
from numistalib.models.base.base_model import NumistaBaseModel


class OAuthToken(NumistaBaseModel):
    """OAuth access token response.

    Matches the `/oauth_token` response shape in the Numista Swagger.

    Parameters
    ----------
    access_token : str
        Token granting access to user endpoints.
    token_type : str
        Token type (typically "bearer").
    expires_in : int
        Lifetime in seconds.
    user_id : int
        ID of the authenticated user.
    """

    access_token: str
    token_type: str
    expires_in: int
    user_id: int

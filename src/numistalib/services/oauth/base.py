"""Abstract base classes for OAuth service."""

from abc import abstractmethod

from numistalib.models.oauth import OAuthToken
from numistalib.services.base import BaseService


class OAuthServiceBase(BaseService):
    """Abstract interface for OAuth token operations."""

    @abstractmethod
    def get_token_client_credentials(self, scope: str) -> OAuthToken:
        """Get an OAuth token using the client credentials grant."""
        pass

    @abstractmethod
    async def get_token_client_credentials_async(self, scope: str) -> OAuthToken:
        """Get an OAuth token using the client credentials grant (async)."""
        pass

    @abstractmethod
    def exchange_authorization_code(
        self,
        *,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> OAuthToken:
        """Exchange an authorization code for an access token."""
        pass

    @abstractmethod
    async def exchange_authorization_code_async(
        self,
        *,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> OAuthToken:
        """Exchange an authorization code for an access token (async)."""
        pass

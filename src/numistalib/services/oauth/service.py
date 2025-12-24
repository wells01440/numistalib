"""OAuth service implementation."""

from __future__ import annotations

# Standard library
from collections.abc import Mapping
from typing import Any, cast

# Local
from numistalib import logger
from numistalib.client import NumistaResponse
from numistalib.models.oauth import OAuthToken
from numistalib.services.oauth.base import OAuthServiceBase


class OAuthService(OAuthServiceBase):
    """Service for `/oauth_token` endpoints."""

    def _to_models(self, items: list[Mapping[str, Any]], **kwargs: Any) -> list[OAuthToken]:
        _ = kwargs
        logger.debug("→ %s._to_models(items=%s)", self.__class__.__name__, len(items))
        return [OAuthToken.model_validate(item) for item in items]

    def get_token_client_credentials(self, scope: str) -> OAuthToken:
        logger.debug("→ get_token_client_credentials(scope=%s)", scope)

        params = self._build_params(grant_type="client_credentials", scope=scope)
        response = cast(NumistaResponse, self._client.get("/oauth_token", params=params))
        response.raise_for_status()
        self._track_response(response)

        data = cast(Mapping[str, Any], response.json())
        token = OAuthToken.model_validate(data)
        logger.info(f"Retrieved OAuth token for user {token.user_id} {response.cached_indicator}")
        return token

    async def get_token_client_credentials_async(self, scope: str) -> OAuthToken:
        logger.debug("→ get_token_client_credentials_async(scope=%s)", scope)

        params = self._build_params(grant_type="client_credentials", scope=scope)
        response = await self._aget("/oauth_token", params=params)
        response.raise_for_status()

        data = cast(Mapping[str, Any], response.json())
        token = OAuthToken.model_validate(data)
        logger.info(f"Retrieved OAuth token for user {token.user_id} {response.cached_indicator}")
        return token

    def exchange_authorization_code(
        self,
        *,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> OAuthToken:
        logger.debug("→ exchange_authorization_code(client_id=%s)", client_id)

        params = self._build_params(
            grant_type="authorization_code",
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
        response = cast(NumistaResponse, self._client.get("/oauth_token", params=params))
        response.raise_for_status()
        self._track_response(response)

        data = cast(Mapping[str, Any], response.json())
        token = OAuthToken.model_validate(data)
        logger.info(f"Exchanged authorization code for user {token.user_id} {response.cached_indicator}")
        return token

    async def exchange_authorization_code_async(
        self,
        *,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> OAuthToken:
        logger.debug("→ exchange_authorization_code_async(client_id=%s)", client_id)

        params = self._build_params(
            grant_type="authorization_code",
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
        response = await self._aget("/oauth_token", params=params)
        response.raise_for_status()

        data = cast(Mapping[str, Any], response.json())
        token = OAuthToken.model_validate(data)
        logger.info(f"Exchanged authorization code for user {token.user_id} {response.cached_indicator}")
        return token

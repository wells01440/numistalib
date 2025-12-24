"""Configuration settings for numistalib.

Manages API keys, cache settings, rate limits via Pydantic BaseSettings.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from numistalib.client import NumistaClientAsync, NumistaClientSync

if TYPE_CHECKING:
    from numistalib.models.oauth import OAuthToken


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    Parameters
    ----------
    api_key : str | None
        Numista API key (loaded from env by default; can be provided explicitly elsewhere)
    api_base_url : str
        Base URL for Numista API
    cache_dir : Path
        Directory for persistent HTTP cache
    cache_ttl_types : int
        Cache TTL for type endpoints (seconds)
    cache_ttl_catalogues : int
        Cache TTL for catalogue endpoints (seconds)
    cache_ttl_prices : int
        Cache TTL for price endpoints (seconds)
    rate_limit_requests : int
        Maximum requests per minute
    rate_limit_period : int
        Rate limit period in seconds
    retry_attempts : int
        Maximum retry attempts for failed requests
    retry_max_wait : int
        Maximum wait time between retries (seconds)
    log_level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Examples
    --------
    >>> settings = Settings(api_key="your_key_here")
    >>> print(settings.api_base_url)
    https://api.numista.com/v3
    """

    @staticmethod
    def get_environment_file() -> Path | None:
        """Find and return the path to the environment file.

        Looks in the following locations in order:
        1. .env in current working directory
        2. .env in project root
        3. .numistalib.env in home directory
        4. /etc/numistalib.env

        Returns
        -------
        Path | None
            Path to environment file if found, else None
        """
        project_root = Path(__file__).resolve().parents[2]
        cwd_env = Path.cwd() / ".env"
        if cwd_env.is_file():
            return cwd_env
        project_env = project_root / ".env"
        if project_env.is_file():
            return project_env
        home_env = Path.home() / ".numistalib.env"
        if home_env.is_file():
            return home_env
        etc_env = Path("/etc/numistalib.env")
        if etc_env.is_file():
            return etc_env
        return None

    @staticmethod
    def save_oauth_token(token: str, env_path: Path | None = None) -> Path:
        """Persist the OAuth token to the discovered env file.

        Parameters
        ----------
        token : str
            OAuth access token to persist.
        env_path : Path | None
            Optional explicit env file path; defaults to the discovered env file.

        Returns
        -------
        Path
            Path to the env file that was updated.
        """

        env_file = env_path or Settings.get_environment_file()
        if env_file is None:
            raise FileNotFoundError("No environment file found to store OAuth token")

        lines = env_file.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        token_written = False

        for line in lines:
            if line.startswith("NUMISTA_OAUTH_ACCESS_TOKEN="):
                new_lines.append(f"NUMISTA_OAUTH_ACCESS_TOKEN={token}")
                token_written = True
            else:
                new_lines.append(line)

        if not token_written:
            new_lines.append(f"NUMISTA_OAUTH_ACCESS_TOKEN={token}")

        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return env_file

    model_config = SettingsConfigDict(
        env_file=get_environment_file(),
        env_file_encoding="utf-8",
        env_prefix="NUMISTA_",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_key: str | None = Field(
        default=None,
        description=("Numista API key; read from environment (.env) by default and may be provided explicitly"),
    )

    client_id: str | None = Field(
        default=None,
        description=(
            "OAuth client ID assigned to your application by Numista. "
            "Set via NUMISTA_CLIENT_ID (used when generating OAuth authorization URLs / token exchange)."
        ),
    )

    client_name: str | None = Field(
        default=None,
        description=(
            "Optional application label / client name for local convenience. "
            "Set via NUMISTA_CLIENT_NAME."
        ),
    )

    def build_oauth_authorize_url(
        self,
        *,
        redirect_uri: str,
        scope: str | list[str],
        state: str,
        language: str = "en",
    ) -> str:
        """Build the Numista OAuth authorize URL.

        Parameters
        ----------
        redirect_uri : str
            Redirect URI registered for your application.
        scope : str | list[str]
            OAuth scopes to request (comma-separated string or list).
        state : str
            CSRF protection state; verify it matches on redirect.
        language : str
            Numista language subdomain ("en", "fr", or "es").

        Returns
        -------
        str
            Fully-qualified authorization URL to open in a browser.
        """
        if self.client_id is None or not self.client_id.strip():
            raise ValueError("NUMISTA_CLIENT_ID is required to build the OAuth authorize URL")

        language_normalized = language.strip().lower()
        if language_normalized not in {"en", "fr", "es"}:
            raise ValueError("language must be one of: en, fr, es")

        scope_value = ",".join(scope) if isinstance(scope, list) else scope
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": scope_value,
                "state": state,
            }
        )
        return f"https://{language_normalized}.numista.com/api/oauth_authorize.php?{query}"

    def get_oauth_token_client_credentials(self, *, scope: str | list[str]) -> OAuthToken:
        """Get an OAuth access token using the client credentials grant (sync).

        Notes
        -----
        This uses `/oauth_token?grant_type=client_credentials`.
        """
        scope_value = ",".join(scope) if isinstance(scope, list) else scope
        client = Settings.to_client(self)
        oauth_module = import_module("numistalib.services.oauth")
        oauth_service_cls = cast(object, oauth_module.OAuthService)
        service = oauth_service_cls(client)
        return service.get_token_client_credentials(scope=scope_value)

    async def get_oauth_token_client_credentials_async(self, *, scope: str | list[str]) -> OAuthToken:
        """Get an OAuth access token using the client credentials grant (async)."""
        scope_value = ",".join(scope) if isinstance(scope, list) else scope
        client = Settings.to_async_client(self)
        oauth_module = import_module("numistalib.services.oauth")
        oauth_service_cls = cast(object, oauth_module.OAuthService)
        service = oauth_service_cls(client)
        return await service.get_token_client_credentials_async(scope=scope_value)

    def exchange_oauth_authorization_code(self, *, code: str, redirect_uri: str) -> OAuthToken:
        """Exchange an authorization code for an OAuth access token (sync)."""
        if self.client_id is None or not self.client_id.strip():
            raise ValueError("NUMISTA_CLIENT_ID is required to exchange an authorization code")
        if self.api_key is None or not self.api_key.strip():
            raise ValueError("NUMISTA_API_KEY is required to exchange an authorization code")

        client = Settings.to_client(self)
        oauth_module = import_module("numistalib.services.oauth")
        oauth_service_cls = cast(object, oauth_module.OAuthService)
        service = oauth_service_cls(client)
        return service.exchange_authorization_code(
            code=code,
            client_id=self.client_id,
            client_secret=self.api_key,
            redirect_uri=redirect_uri,
        )

    async def exchange_oauth_authorization_code_async(self, *, code: str, redirect_uri: str) -> OAuthToken:
        """Exchange an authorization code for an OAuth access token (async)."""
        if self.client_id is None or not self.client_id.strip():
            raise ValueError("NUMISTA_CLIENT_ID is required to exchange an authorization code")
        if self.api_key is None or not self.api_key.strip():
            raise ValueError("NUMISTA_API_KEY is required to exchange an authorization code")

        client = Settings.to_async_client(self)
        oauth_module = import_module("numistalib.services.oauth")
        oauth_service_cls = cast(object, oauth_module.OAuthService)
        service = oauth_service_cls(client)
        return await service.exchange_authorization_code_async(
            code=code,
            client_id=self.client_id,
            client_secret=self.api_key,
            redirect_uri=redirect_uri,
        )

    oauth_access_token: str | None = Field(
        default=None,
        description=(
            "Optional OAuth 2.0 access token for user endpoints. "
            "Set via NUMISTA_OAUTH_ACCESS_TOKEN to access /users/*/collections and /users/*/collected_items."
        ),
    )
    api_base_url: str = Field(
        default="https://api.numista.com/v3",
        description="Base URL for Numista API",
    )
    timeout: float = Field(
        default=30.0,
        description="HTTP request timeout in seconds",
    )

    # Cache Configuration
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".cache/numistalib/hishel",
        description="Directory for persistent HTTP cache",
    )
    cache_db_name: str = Field(
        default="hishel_cache.db",
        description="Name of the cache database file",
    )
    cache_ttl_types: int = Field(
        default=604800,  # 7 days
        description="Cache TTL for type endpoints (seconds)",
    )
    cache_ttl_catalogues: int = Field(
        default=604800,  # 7 days
        description="Cache TTL for catalogue endpoints (seconds)",
    )
    cache_ttl_prices: int = Field(
        default=86400,  # 1 day
        description="Cache TTL for price endpoints (seconds)",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=45,
        description="Maximum requests per minute",
    )
    rate_limit_period: int = Field(
        default=60,
        description="Rate limit period in seconds",
    )

    # Retry Configuration
    retry_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests",
    )
    retry_max_wait: int = Field(
        default=10,
        description="Maximum wait time between retries (seconds)",
    )

    # Cache Policy
    cache_allow_stale: bool = Field(
        default=True,
        description="Allow serving stale responses from cache",
    )
    cache_shared: bool = Field(
        default=True,
        description="Use shared (public) cache vs private cache",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    @classmethod
    def to_client(cls, settings: Settings) -> NumistaClientSync:
        """Create a synchronous Numista client from a `Settings` instance.

        Parameters
        ----------
        settings : Settings
            Configuration settings to build the client.

        Returns
        -------
        NumistaClientSync
            Configured synchronous HTTP client.

        Examples
        --------
        >>> s = Settings()
        >>> client = Settings.to_client(s)
        """
        return NumistaClientSync(
            api_key=settings.api_key,
            oauth_access_token=settings.oauth_access_token,
            api_base_url=settings.api_base_url,
            timeout=settings.timeout,
            database_cache_dir=str(settings.cache_dir),
            database_cache_db=settings.cache_db_name,
            rate_limit_requests=settings.rate_limit_requests,
            rate_limit_period=settings.rate_limit_period,
        )

    @classmethod
    def to_async_client(cls, settings: Settings) -> NumistaClientAsync:
        """Create an asynchronous Numista client from a `Settings` instance.

        Parameters
        ----------
        settings : Settings
            Configuration settings to build the client.

        Returns
        -------
        NumistaClientAsync
            Configured asynchronous HTTP client.

        Examples
        --------
        >>> s = Settings()
        >>> client = Settings.to_async_client(s)
        """
        return NumistaClientAsync(
            api_key=settings.api_key,
            oauth_access_token=settings.oauth_access_token,
            api_base_url=settings.api_base_url,
            timeout=settings.timeout,
            database_cache_dir=str(settings.cache_dir),
            database_cache_db=settings.cache_db_name,
            rate_limit_requests=settings.rate_limit_requests,
            rate_limit_period=settings.rate_limit_period,
        )


# get_settings() has been removed in favor of directly instantiating `Settings()`.


# The helper functions `create_client_from_settings()` and
# `create_async_client_from_settings()` were removed. Use
# `Settings.to_client(Settings())` or `Settings.to_async_client(Settings())`.

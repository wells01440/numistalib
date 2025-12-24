"""OAuth CLI commands."""

from __future__ import annotations

# Third-party
import click
from httpx import HTTPStatusError

# Local
from numistalib.cli.theme import CLISettings
from numistalib.config import Settings


def register_oauth_commands(parent: click.Group) -> None:
    """Register OAuth commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to.
    """

    @click.command(name="token")
    @click.option(
        "-s",
        "--scope",
        multiple=True,
        type=click.Choice(["view_collection", "edit_collection"]),
        default=("view_collection",),
        show_default=True,
        help="OAuth scope(s) to request.",
    )
    def oauth_token(scope: tuple[str, ...]) -> None:
        """Fetch an OAuth token using client credentials.

        Examples
        --------
        numistalib oauth token --scope view_collection
        numistalib oauth token -s view_collection -s edit_collection
        """
        console = CLISettings.console()
        settings = Settings()

        try:
            token = settings.get_oauth_token_client_credentials(scope=list(scope))
        except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
            console.print(f"[danger]Error fetching OAuth token: {err}[/danger]")
            return

        console.print(token.render_panel(title="OAuth Token"))
        console.print(
            f'[success]export NUMISTA_OAUTH_ACCESS_TOKEN="{token.access_token}"[/success]'
        )
        console.print(CLISettings.LICENSE_TEXT, style="footer")

    @click.command(name="exchange-code")
    @click.option("--code", type=str, required=True, help="Authorization code returned by Numista")
    @click.option(
        "--redirect-uri",
        type=str,
        required=True,
        help="The redirect URI used when generating the authorize URL",
    )
    def oauth_exchange_code(code: str, redirect_uri: str) -> None:
        """Exchange an authorization code for an OAuth token.

        Notes
        -----
        Requires `NUMISTA_CLIENT_ID` and `NUMISTA_API_KEY` (used as client secret).

        Examples
        --------
        numistalib oauth exchange-code --code ABC --redirect-uri https://example.com/callback
        """
        console = CLISettings.console()
        settings = Settings()

        try:
            token = settings.exchange_oauth_authorization_code(code=code, redirect_uri=redirect_uri)
        except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
            console.print(f"[danger]Error exchanging authorization code: {err}[/danger]")
            return

        console.print(token.render_panel(title="OAuth Token"))
        console.print(
            f'[success]export NUMISTA_OAUTH_ACCESS_TOKEN="{token.access_token}"[/success]'
        )
        console.print(CLISettings.LICENSE_TEXT, style="footer")

    oauth_group = click.Group(name="oauth", help="OAuth helpers (token acquisition)")
    oauth_group.add_command(oauth_token)
    oauth_group.add_command(oauth_exchange_code)
    parent.add_command(oauth_group)

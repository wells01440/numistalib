"""Mints CLI commands."""

import sys

import click

from numista_lib import logger
from numista_lib.cli.theme import CLISettings
from numista_lib.config import create_client_from_settings, get_settings
from numista_lib.services import MintService


def register_mints_commands(parent: click.Group) -> None:
    """Register mints commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command()
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def mints(lang: str) -> None:
        """List all mints.

        Examples:
            numista-lib mints
            numista-lib mints --lang es
        """
        try:
            settings = get_settings()
            client = create_client_from_settings(settings)
            service = MintService(client)
            model_cls = getattr(service, "MODEL", None)
            model_label = model_cls.__name__ if model_cls else "Mint"

            CLISettings.console().print(
                CLISettings.header_panel(f"Mints [{model_label}]")
            )
            results = service.get_mints(lang=lang)

            if not results:
                CLISettings.console().print("[warning]No mints found[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return

            table = CLISettings.create_table("Mints")
            CLISettings.table_add_columns(
                table,
                [
                    "Cache",
                    "ID",
                    "Name",
                    "Code",
                    "Country Code",
                ],
            )

            cache_icon = service.last_cache_indicator
            for mint in results:
                CLISettings.table_add_row(
                    table,
                    [
                        cache_icon,
                        mint.numista_id,
                        mint.name,
                        mint.code or "",
                        mint.country_code or "",
                    ],
                )

            CLISettings.console().print(table)
            CLISettings.console().print(f"\n[success]Found {len(results)} mints[/success]")
            CLISettings.console().print(CLISettings.footer_panel())

        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception("Error listing mints")
            sys.exit(1)

"""Issuers CLI commands."""

import asyncio
import sys

import click

from numistalib import logger
from numistalib.cli.theme import CLISettings
from numistalib.config import create_async_client_from_settings, get_settings
from numistalib.services import IssuerService


def register_issuers_commands(parent: click.Group) -> None:
    """Register issuers commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command()
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    @click.option("--limit", type=int, default=50, help="Results per page")
    def issuers(lang: str, limit: int) -> None:
        """List all issuing countries and territories.

        Issuers are countries, territories, and political entities that issue currency.
        This is different from 'issues', which are production variants (year/mint) of types.

        Iterates through all pages automatically.

        Examples:
            numistalib issuers
            numistalib issuers --lang es --limit 100
        """
        try:
            settings = get_settings()
            client = create_async_client_from_settings(settings)
            service = IssuerService(client)
            model_cls = service.MODEL
            model_label = model_cls.__name__ if model_cls else "Issuer"

            CLISettings.console().print(
                CLISettings.header_panel(f"Issuers [{model_label}]")
            )

            table = CLISettings.table_from_model_class(
                model_cls,
                include_cache=True,
                title="Issuers (Paginated)",
            )

            count = 0

            async def consume_issuers() -> None:
                nonlocal count
                async for issuer in service.get_issuers_paginated(lang=lang, limit=limit):
                    count += 1
                    CLISettings.table_add_model_row(
                        table,
                        issuer,
                        include_cache=True,
                        cache_icon=service.last_cache_indicator,
                    )

            asyncio.run(consume_issuers())

            if count == 0:
                CLISettings.console().print("[warning]No issuers found[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return
            CLISettings.console().print(table)
            CLISettings.console().print(f"\n[success]Found {count} issuers[/success]")
            CLISettings.console().print(CLISettings.footer_panel())

        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception("Error listing issuers")
            sys.exit(1)

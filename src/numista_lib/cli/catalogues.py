"""Catalogues CLI commands."""

import sys

import click

from numista_lib import logger
from numista_lib.cli.theme import CLISettings
from numista_lib.config import create_client_from_settings, get_settings
from numista_lib.services import CatalogueService


def register_catalogues_commands(parent: click.Group) -> None:
    """Register catalogues commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command()
    def catalogues() -> None:
        """List all reference catalogues.

        Examples:
            numista-lib catalogues
        """
        try:
            settings = get_settings()
            client = create_client_from_settings(settings)
            service = CatalogueService(client)
            model_cls = service.MODEL
            model_label = model_cls.__name__ if model_cls else "Catalogue"

            CLISettings.console().print(
                CLISettings.header_panel(f"Catalogues [{model_label}]")
            )
            results = service.get_catalogues()
            table = CLISettings.table_from_model_class(
                model_cls,
                include_cache=True,
                title="Reference Catalogues",
            )

            if not results:
                CLISettings.console().print("[warning]No catalogues found[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return

            cache_icon = service.last_cache_indicator
            for catalogue in results:
                CLISettings.table_add_model_row(
                    table,
                    catalogue,
                    include_cache=True,
                    cache_icon=cache_icon,
                )

            CLISettings.console().print(table)
            CLISettings.console().print(
                f"\n[success]Found {len(results)} catalogues[/success]"
            )
            CLISettings.console().print(CLISettings.footer_panel())

        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception("Error listing catalogues")
            sys.exit(1)

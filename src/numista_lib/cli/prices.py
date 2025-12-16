"""Prices CLI commands."""

import sys

import click

from numista_lib import logger
from numista_lib.cli.theme import CLISettings
from numista_lib.config import create_client_from_settings, get_settings
from numista_lib.services import PriceService


def register_prices_commands(parent: click.Group) -> None:
    """Register prices commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command(name="prices")
    @click.argument("type_id", type=int)
    @click.argument("issue_id", type=int)
    def prices(type_id: int, issue_id: int) -> None:
        """Get price estimates for an issue.

        Examples:
            numista-lib prices 95420 123456
        """
        try:
            settings = get_settings()
            client = create_client_from_settings(settings)
            service = PriceService(client)

            model_cls = service.MODEL
            model_label = model_cls.__name__ if model_cls else "Price"

            CLISettings.console().print(
                CLISettings.header_panel(f"Prices [{model_label}]: Type {type_id}, Issue {issue_id}")
            )

            prices = service.get_prices(type_id=type_id, issue_id=issue_id)

            table = CLISettings.table_from_model_class(
                model_cls,
                include_cache=True,
                title=f"Prices for Type {type_id}, Issue {issue_id}",
            )

            if not prices:
                CLISettings.console().print(f"[warning]No prices found for type {type_id}, issue {issue_id}[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return
            for price in prices:
                CLISettings.table_add_model_row(table, price)
            CLISettings.console().print(table)
            CLISettings.console().print(f"\n[success]Found {len(prices)} price estimates[/success]")
            CLISettings.console().print(CLISettings.footer_panel())
        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception(f"Error getting prices for type {type_id}, issue {issue_id}")
            sys.exit(1)

"""Configuration management CLI commands."""

import sys

import click

from numista_lib.cli.theme import CLISettings
from numista_lib.config import get_settings


def register_config_commands(parent: click.Group) -> None:
    """Register config commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def config() -> None:
        """Manage configuration settings."""
        pass

    @config.command(name="get")
    @click.argument("key")
    def config_get(key: str) -> None:
        """Get a configuration value.

        Examples:
            numista-lib config get api_key
            numista-lib config get cache_dir
        """
        try:
            console = CLISettings.console()
            console.print(CLISettings.header_panel("Configuration"))
            settings = get_settings()
            value = getattr(settings, key.lower(), None)
            if value is None:
                console.print(f"[danger]Setting '{key}' not found[/danger]")
                sys.exit(1)
            console.print(f"[header]{key}:[/header] {value}")
            console.print(CLISettings.footer_panel())
        except (AttributeError, ValueError, KeyError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            sys.exit(1)

    @config.command(name="list")
    def config_list() -> None:
        """List all configuration settings."""
        try:
            console = CLISettings.console()
            console.print(CLISettings.header_panel("Configuration"))
            settings = get_settings()
            table = CLISettings.create_table("Numista-lib Configuration")
            CLISettings.table_add_columns(
                table,
                ["Setting", "Value"]
            )

            for field_name in type(settings).model_fields:
                value = getattr(settings, field_name)
                if field_name == "api_key":
                    value = "***" if value else None
                CLISettings.table_add_row(table, [field_name, value])

            console.print(table)
            console.print(CLISettings.footer_panel())
        except (AttributeError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            sys.exit(1)

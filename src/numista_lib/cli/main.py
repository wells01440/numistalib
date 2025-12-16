"""Command-line interface main entry point for numista-lib.

Registers all CLI command groups.
"""

import click

from numista_lib.cli.catalogues import register_catalogues_commands
from numista_lib.cli.collections import register_collections_commands
from numista_lib.cli.config import register_config_commands
from numista_lib.cli.image_search import register_image_search_commands
from numista_lib.cli.issuers import register_issuers_commands
from numista_lib.cli.issues import register_issues_commands
from numista_lib.cli.literature import register_literature_commands
from numista_lib.cli.mints import register_mints_commands
from numista_lib.cli.prices import register_prices_commands
from numista_lib.cli.types import register_types_commands
from numista_lib.cli.users import register_users_commands


@click.group()
@click.version_option(version="0.1.0", prog_name="numista-lib")
def cli() -> None:
    """Numista API wrapper - search and manage numismatic data."""
    pass


def main() -> None:
    """Register all command groups and run CLI."""
    register_config_commands(cli)
    register_types_commands(cli)
    register_catalogues_commands(cli)
    register_issuers_commands(cli)
    register_issues_commands(cli)
    register_mints_commands(cli)
    register_collections_commands(cli)
    register_image_search_commands(cli)
    register_literature_commands(cli)
    register_prices_commands(cli)
    register_users_commands(cli)
    cli()


if __name__ == "__main__":
    main()

"""Literature CLI commands."""

import click

from numista_lib.cli.theme import CLISettings


def register_literature_commands(parent: click.Group) -> None:
    """Register literature commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def literature() -> None:
        """Access numismatic literature catalogue."""
        pass

    @literature.command(name="get")
    @click.argument("publication_id", type=int)
    def literature_get(_publication_id: int) -> None:
        """Get details about a publication.

        Examples:
            numista-lib literature get 12345
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Literature commands not yet implemented[/warning]")

    @literature.command(name="search")
    @click.option("-q", "--query", required=True, help="Search query")
    def literature_search(_query: str) -> None:
        """Search literature catalogue.

        Examples:
            numista-lib literature search -q "Krause"
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Literature commands not yet implemented[/warning]")

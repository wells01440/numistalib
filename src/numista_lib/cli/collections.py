"""Collections CLI commands."""

import click

from numista_lib.cli.theme import CLISettings


def register_collections_commands(parent: click.Group) -> None:
    """Register collections commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def collections() -> None:
        """Manage user collections."""
        pass

    @collections.command(name="list")
    @click.argument("user_id", type=int)
    def collections_list(_user_id: int) -> None:
        """List collections for a user.

        Examples:
            numista-lib collections list 12345
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Collections commands require OAuth authentication (not yet implemented)[/warning]")

    @collections.command(name="items")
    @click.argument("user_id", type=int)
    @click.option("--collection-id", type=int, help="Filter by collection ID")
    def collections_items(_user_id: int, _collection_id: int | None) -> None:
        """List items in a user's collection.

        Examples:
            numista-lib collections items 12345
            numista-lib collections items 12345 --collection-id 67890
        """
        CLISettings.console()
        CLISettings.console().print("[warning]Collections commands require OAuth authentication (not yet implemented)[/warning]")

"""Users CLI commands."""

# pyright: reportUnusedFunction=false, reportUnusedVariable=false

# Standard library
from collections.abc import Mapping
from typing import Any, cast

# Third-party
import click
from httpx import HTTPStatusError
from rich.panel import Panel
from rich.table import Table

# Local
from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.services.users.service import UserService

# pyright: reportUnusedFunction=false


def register_users_commands(parent: click.Group) -> None:
    """Register users commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @click.command(name="get")
    @click.argument("user_id", type=int)
    def users_get(user_id: int) -> None:
        """Get details about a user.

        Examples:
            numistalib users get 12345
        """
        _handle_users_get(user_id)

    @click.command(name="collections")
    @click.argument("user_id", type=int)
    def users_collections(user_id: int) -> None:
        """List collections for a user.

        Requires OAuth with view_collection scope.

        Examples:
            numistalib users collections 12345
        """
        _handle_users_collections(user_id)

    @click.command(name="items")
    @click.argument("user_id", type=int)
    @click.option(
        "-c",
        "--category",
        type=click.Choice(["coin", "banknote", "exonumia"]),
        help="Filter by category",
    )
    @click.option("-t", "--type-id", type=int, help="Filter by type ID")
    @click.option("--collection-id", type=int, help="Filter by collection ID")
    @click.option(
        "--limit",
        type=int,
        default=50,
        help="Maximum results to display",
    )
    def users_items(
        user_id: int,
        category: str | None,
        type_id: int | None,
        collection_id: int | None,
        limit: int,
    ) -> None:
        """List collected items for a user.

        Requires OAuth with view_collection scope.

        Examples:
            numistalib users items 12345
            numistalib users items 12345 --category coin
            numistalib users items 12345 --type-id 95420
        """
        _handle_users_items(user_id, category, type_id, collection_id, limit)

    @click.command(name="item-get")
    @click.argument("user_id", type=int)
    @click.argument("item_id", type=int)
    def users_item_get(user_id: int, item_id: int) -> None:
        """Get a collected item by ID.

        Requires OAuth with view_collection scope.

        Examples:
            numistalib users item-get 12345 987
        """
        _handle_users_item_get(user_id, item_id)

    @click.command(name="item-add")
    @click.argument("user_id", type=int)
    @click.option("--type-id", type=int, required=True, help="Numista type id")
    @click.option("--issue-id", type=int, help="Issue id")
    @click.option("--collection-id", type=int, help="Collection id")
    @click.option("--quantity", type=int, help="Quantity")
    @click.option("--grade", type=str, help="Grade")
    @click.option("--for-swap/--not-for-swap", default=False, help="Mark item for swap")
    @click.option("--private-comment", type=str, help="Private comment")
    @click.option("--public-comment", type=str, help="Public comment")
    def users_item_add(  # noqa: PLR0913, PLR0917
        user_id: int,
        type_id: int,
        issue_id: int | None,
        collection_id: int | None,
        quantity: int | None,
        grade: str | None,
        for_swap: bool,
        private_comment: str | None,
        public_comment: str | None,
    ) -> None:
        """Add a collected item.

        Requires OAuth with edit_collection scope.

        Examples:
            numistalib users item-add 12345 --type-id 95420 --quantity 1
        """
        ctx = click.get_current_context()
        payload = _build_collected_item_payload_from_params(ctx.params)
        _handle_users_item_add(user_id, payload)

    @click.command(name="item-edit")
    @click.argument("user_id", type=int)
    @click.argument("item_id", type=int)
    @click.option("--issue-id", type=int, help="Issue id")
    @click.option("--collection-id", type=int, help="Collection id")
    @click.option("--quantity", type=int, help="Quantity")
    @click.option("--grade", type=str, help="Grade")
    @click.option("--for-swap/--not-for-swap", default=False, help="Mark item for swap")
    @click.option("--private-comment", type=str, help="Private comment")
    @click.option("--public-comment", type=str, help="Public comment")
    def users_item_edit(  # noqa: PLR0913, PLR0917
        user_id: int,
        item_id: int,
        issue_id: int | None,
        collection_id: int | None,
        quantity: int | None,
        grade: str | None,
        for_swap: bool,
        private_comment: str | None,
        public_comment: str | None,
    ) -> None:
        """Edit a collected item.

        Requires OAuth with edit_collection scope.

        Examples:
            numistalib users item-edit 12345 987 --quantity 2
        """
        ctx = click.get_current_context()
        payload = _build_collected_item_payload_from_params(ctx.params)
        payload.pop("type", None)
        _handle_users_item_edit(user_id, item_id, payload)

    @click.command(name="item-delete")
    @click.argument("user_id", type=int)
    @click.argument("item_id", type=int)
    @click.confirmation_option(prompt="Are you sure you want to delete this collected item?")
    def users_item_delete(user_id: int, item_id: int) -> None:
        """Delete a collected item.

        Requires OAuth with edit_collection scope.

        Examples:
            numistalib users item-delete 12345 987
        """
        _handle_users_item_delete(user_id, item_id)

    users_group = click.Group(name="users", help="Access user information and collections")
    users_group.add_command(users_get)
    users_group.add_command(users_collections)
    users_group.add_command(users_items)
    users_group.add_command(users_item_get)
    users_group.add_command(users_item_add)
    users_group.add_command(users_item_edit)
    users_group.add_command(users_item_delete)
    parent.add_command(users_group)


def _build_collected_item_payload_from_params(params: Mapping[str, Any]) -> dict[str, object]:
    payload: dict[str, object] = {}

    type_id = params.get("type_id")
    if type_id is not None:
        payload["type"] = cast(int, type_id)

    issue_id = params.get("issue_id")
    if issue_id is not None:
        payload["issue"] = cast(int, issue_id)

    collection_id = params.get("collection_id")
    if collection_id is not None:
        payload["collection"] = cast(int, collection_id)

    quantity = params.get("quantity")
    if quantity is not None:
        payload["quantity"] = cast(int, quantity)

    grade = params.get("grade")
    if grade is not None:
        payload["grade"] = cast(str, grade)

    if params.get("for_swap"):
        payload["for_swap"] = True

    private_comment = params.get("private_comment")
    if private_comment is not None:
        payload["private_comment"] = cast(str, private_comment)

    public_comment = params.get("public_comment")
    if public_comment is not None:
        payload["public_comment"] = cast(str, public_comment)

    return payload


def _require_oauth(console: object) -> bool:
    settings = Settings()
    if settings.oauth_access_token is None:
        console.print(
            "[warning]OAuth required. Set NUMISTA_OAUTH_ACCESS_TOKEN to use this command.[/warning]"
        )
        return False
    return True


def _handle_users_item_get(user_id: int, item_id: int) -> None:
    console = CLISettings.console()
    if not _require_oauth(console):
        return

    settings = Settings()
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        item = service.get_collected_item(user_id=user_id, item_id=item_id)

        panel_content = f"""
[bold]ID:[/bold] {item.id}
[bold]Type:[/bold] {item.type.title}
[bold]Category:[/bold] {item.type.category}
[bold]Quantity:[/bold] {item.quantity}
[bold]Grade:[/bold] {item.grade or '—'}
[bold]For Swap:[/bold] {'Yes' if item.for_swap else 'No'}
""".strip()
        panel = Panel(
            panel_content,
            title=f"[bold]Collected Item {item_id}[/bold]",
            width=80,
            border_style="cyan",
        )
        console.print(panel)
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error retrieving collected item {item_id} for user {user_id}: {err}[/error]",
            style="red",
        )


def _handle_users_item_add(user_id: int, payload: dict[str, object]) -> None:
    console = CLISettings.console()
    if not _require_oauth(console):
        return

    settings = Settings()
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        item = service.add_collected_item(user_id=user_id, payload=payload)

        panel = Panel(
            f"Added collected item [bold]{item.id}[/bold]",
            title="[bold]Success[/bold]",
            width=80,
            border_style="green",
        )
        console.print(panel)
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error adding collected item for user {user_id}: {err}[/error]",
            style="red",
        )


def _handle_users_item_edit(user_id: int, item_id: int, payload: dict[str, object]) -> None:
    console = CLISettings.console()
    if not _require_oauth(console):
        return
    if not payload:
        console.print("[error]No fields to update.[/error]", style="red")
        return

    settings = Settings()
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        item = service.edit_collected_item(user_id=user_id, item_id=item_id, payload=payload)

        panel = Panel(
            f"Updated collected item [bold]{item.id}[/bold]",
            title="[bold]Success[/bold]",
            width=80,
            border_style="green",
        )
        console.print(panel)
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error editing collected item {item_id} for user {user_id}: {err}[/error]",
            style="red",
        )


def _handle_users_item_delete(user_id: int, item_id: int) -> None:
    console = CLISettings.console()
    if not _require_oauth(console):
        return

    settings = Settings()
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        service.delete_collected_item(user_id=user_id, item_id=item_id)
        console.print(
            f"[green]Deleted[/green] collected item {item_id} for user {user_id}",
        )
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error deleting collected item {item_id} for user {user_id}: {err}[/error]",
            style="red",
        )


def _handle_users_get(user_id: int) -> None:
    """Handle users get command.

    Parameters
    ----------
    user_id : int
        User ID to retrieve
    """
    console = CLISettings.console()
    settings = Settings()
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        user = service.get_user(user_id)

        panel_content = f"""
[bold]Username:[/bold] {user.username}
[bold]Member Since:[/bold] {user.member_since or 'N/A'}
[bold]Country:[/bold] {user.country_code or 'N/A'}
"""
        if user.avatar:
            panel_content += f"[bold]Avatar:[/bold] {user.avatar}\n"

        panel = Panel(
            panel_content.strip(),
            title=f"[bold]User {user_id}[/bold]",
            width=80,
            border_style="cyan",
        )
        console.print(panel)
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(f"[error]Error retrieving user {user_id}: {err}[/error]", style="red")


def _handle_users_collections(user_id: int) -> None:
    """Handle users collections command.

    Parameters
    ----------
    user_id : int
        User ID to retrieve collections for
    """
    console = CLISettings.console()
    settings = Settings()
    if settings.oauth_access_token is None:
        console.print(
            "[warning]OAuth required. Set NUMISTA_OAUTH_ACCESS_TOKEN to use this command.[/warning]"
        )
        return
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        collections = service.get_collections(user_id)

        table = Table(title=f"Collections for User {user_id}", width=80)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Items", style="green", justify="right")

        for coll in collections:
            coll_id = str(coll.get("id", "N/A"))
            name = str(coll.get("name", "N/A"))
            items = str(coll.get("number_of_items", "0"))
            table.add_row(coll_id, name, items)

        console.print(table)
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error retrieving collections for user {user_id}: {err}[/error]",
            style="red",
        )


def _handle_users_items(
    user_id: int,
    category: str | None,
    type_id: int | None,
    collection_id: int | None,
    limit: int,
) -> None:
    """Handle users items command.

    Parameters
    ----------
    user_id : int
        User ID to retrieve items for
    category : str | None
        Category filter
    type_id : int | None
        Type ID filter
    collection_id : int | None
        Collection ID filter
    limit : int
        Maximum results to display
    """
    console = CLISettings.console()
    settings = Settings()
    if settings.oauth_access_token is None:
        console.print(
            "[warning]OAuth required. Set NUMISTA_OAUTH_ACCESS_TOKEN to use this command.[/warning]"
        )
        return
    client = Settings.to_client(settings)
    service = UserService(client)

    try:
        items = service.get_collected_items(
            user_id,
            category=category,
            type_id=type_id,
            collection_id=collection_id,
        )

        display_items = items[:limit]

        table = Table(
            title=f"Collected Items for User {user_id}",
            width=100,
        )
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Category", style="green")
        table.add_column("Qty", style="yellow", justify="right")
        table.add_column("Grade", style="blue")
        table.add_column("For Swap", style="bright_black")

        for item in display_items:
            grade_str = item.grade or "—"
            swap_str = "✓" if item.for_swap else "—"
            table.add_row(
                str(item.id),
                item.type.title,
                item.type.category,
                str(item.quantity),
                grade_str,
                swap_str,
            )

        console.print(table)
        total_shown = len(display_items)
        console.print(
            f"\n[dim]Showing {total_shown} item{'s' if total_shown != 1 else ''}"
            f" (limited to {limit})[/dim]"
        )
        console.print(CLISettings.LICENSE_TEXT, style="footer")
    except (HTTPStatusError, RuntimeError, OSError, ValueError) as err:
        console.print(
            f"[error]Error retrieving items for user {user_id}: {err}[/error]",
            style="red",
        )

"""Issues CLI commands."""

import asyncio
import sys

import click

from numistalib import logger
from numistalib.cli.theme import CLISettings
from numistalib.config import create_async_client_from_settings, get_settings
from numistalib.services import IssueService

COMMENT_MAX_LENGTH = 40


def register_issues_commands(parent: click.Group) -> None:
    """Register issues commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.command()
    @click.argument("type_id", type=int)
    @click.option("--limit", type=int, default=50, help="Results per page")
    def issues(type_id: int, limit: int) -> None:
        """List all issues for a type.

        Issues are production variants (year, mint, mintage, variety) of a catalogue type.
        Each type can have multiple issues. This is different from 'issuers' (countries).

        Iterates through all pages automatically.

        Examples:
            numistalib issues 95420
            numistalib issues 95420 --limit 100
        """
        try:
            settings = get_settings()
            client = create_async_client_from_settings(settings)
            service = IssueService(client)
            model_cls = getattr(service, "MODEL", None)
            model_label = model_cls.__name__ if model_cls else "Issue"

            CLISettings.console().print(
                CLISettings.header_panel(f"Issues [{model_label}] for Type {type_id}")
            )

            table = CLISettings.create_table(f"Issues for Type {type_id}")
            CLISettings.table_add_columns(
                table,
                [
                    "Cache",
                    "ID",
                    "Gregorian Year",
                    "Mint Letter",
                    "Mintage",
                    "Comment",
                ],
            )

            count = 0

            async def consume_issues() -> None:
                nonlocal count
                async for issue in service.get_issues_paginated(type_id=type_id, limit=limit):
                    count += 1
                    comment = issue.comment or ""
                    if len(comment) > COMMENT_MAX_LENGTH:
                        comment = comment[:COMMENT_MAX_LENGTH] + "..."
                    CLISettings.table_add_row(
                        table,
                        [
                            service.last_cache_indicator,
                            issue.numista_id,
                            issue.gregorian_year or "",
                            issue.mint_letter or "",
                            issue.mintage or "",
                            comment,
                        ],
                    )

            asyncio.run(consume_issues())

            if count == 0:
                CLISettings.console().print(f"[warning]No issues found for type {type_id}[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return

            CLISettings.console().print(table)
            CLISettings.console().print(f"\n[success]Found {count} issues[/success]")
            CLISettings.console().print(CLISettings.footer_panel())

        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception(f"Error listing issues for type {type_id}")
            sys.exit(1)

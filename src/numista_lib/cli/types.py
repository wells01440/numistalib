"""Types CLI commands."""

import asyncio
import sys
from typing import Any

import click
from rich.table import Table

from numista_lib import logger
from numista_lib.cli.theme import CLISettings
from numista_lib.config import create_async_client_from_settings, create_client_from_settings, get_settings
from numista_lib.models.types import TypeFull
from numista_lib.services import TypeBasicService, TypeFullService


async def _consume_type_search_results(
    service: TypeBasicService,
    table: Table,
    search_params: dict[str, Any],
) -> int:
    """Consume and display paginated type search results.

    Parameters
    ----------
    service : TypeBasicService
        The type service instance
    table : Table
        Rich table to add rows to
    search_params : dict[str, Any]
        Search parameters (query, issuer, year, category, limit)

    Returns
    -------
    int
        Total count of results
    """
    count = 0
    async for result in service.search_types_paginated(**search_params):
        count += 1
        CLISettings.table_add_model_row(
            table,
            result,
            include_cache=True,
            cache_icon=service.last_cache_indicator,
        )
    return count


def _print_type_details(cache_icon: str, result: TypeFull) -> None:
    """Print detailed type information.

    Parameters
    ----------
    cache_icon : str
        Cache indicator icon
    result : TypeFull
        Full type result object
    """
    CLISettings.console().print(f"\n{cache_icon} [header]Type ID:[/header] {result.numista_id}")
    CLISettings.console().print(f"[header]Title:[/header] {result.title}")
    CLISettings.console().print(f"[header]Category:[/header] {result.category}")
    CLISettings.console().print(f"[header]Issuer:[/header] {result.issuer_name} ({result.issuer_code})")

    if result.value_text:
        CLISettings.console().print(f"[header]Value:[/header] {result.value_text}")
    if result.currency_name:
        CLISettings.console().print(f"[header]Currency:[/header] {result.currency_name}")
    if result.composition:
        CLISettings.console().print(f"[header]Composition:[/header] {result.composition}")
    if result.weight:
        CLISettings.console().print(f"[header]Weight:[/header] {result.weight}g")
    if result.diameter:
        CLISettings.console().print(f"[header]Diameter:[/header] {result.diameter}mm")

    if result.obverse_description:
        CLISettings.console().print(f"[header]Obverse:[/header] {result.obverse_description}")
    if result.reverse_description:
        CLISettings.console().print(f"[header]Reverse:[/header] {result.reverse_description}")


def register_types_commands(parent: click.Group) -> None:
    """Register types commands with parent group.

    Parameters
    ----------
    parent : click.Group
        Parent click group to attach commands to
    """

    @parent.group()
    def types() -> None:
        """Search and retrieve coin/banknote types."""
        pass

    @types.command(name="search")
    @click.option("-q", "--query", help="Full-text search query")
    @click.option("-i", "--issuer", help="Issuer code (e.g., 'united-states')")
    @click.option("-y", "--year", type=int, help="Filter by year")
    @click.option("-c", "--category", type=click.Choice(["coin", "banknote", "exonumia"]), help="Category")
    @click.option("--limit", type=int, default=50, help="Results per page")
    def types_search(
        query: str | None,
        issuer: str | None,
        year: int | None,
        category: str | None,
        limit: int,
    ) -> None:
        """Search the catalogue for types.

        Iterates through all pages automatically.

        Examples:
            numista-lib types search -q "dollar"
            numista-lib types search --issuer united-states --year 2020
            numista-lib types search -q "thaler" --category coin
        """
        try:
            settings = get_settings()
            client = create_async_client_from_settings(settings)
            service = TypeBasicService(client)

            model_cls = getattr(service, "MODEL_BASIC", None)
            model_label = model_cls.__name__ if model_cls else "TypeBasic"

            CLISettings.console().print(
                CLISettings.header_panel(f"Type Search [{model_label}]")
            )
            table = CLISettings.create_table(f"Type Search Results ({model_label})")

            CLISettings.table_add_columns(table, [
                "Cache",
                "ID",
                "Title",
                "Issuer",
                "Years",
                "Category",
            ])

            search_params = {
                "query": query,
                "issuer": issuer,
                "year": year,
                "category": category,
                "limit": limit,
            }
            count = asyncio.run(_consume_type_search_results(service, table, search_params))

            if count == 0:
                CLISettings.console().print("[warning]No results found[/warning]")
                CLISettings.console().print(CLISettings.footer_panel())
                return

            CLISettings.console().print(table)
            CLISettings.console().print(f"\n[success]Found {count} results[/success]")
            CLISettings.console().print(CLISettings.footer_panel())

        except ValueError as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            sys.exit(1)
        except (RuntimeError, OSError) as err:
            CLISettings.console().print(f"[danger]API Error: {err}[/danger]")
            logger.exception("Error during types search")
            sys.exit(1)

    @types.command(name="get")
    @click.argument("type_id", type=int)
    def types_get(type_id: int) -> None:
        """Get details about a specific type.

        Examples:
            numista-lib types get 95420
        """
        try:
            CLISettings.console().print(CLISettings.header_panel(f"Type Details: {type_id}"))
            settings = get_settings()
            client = create_client_from_settings(settings)
            service = TypeFullService(client)
            result = service.get_type(type_id)
            cache_icon = service.last_cache_indicator
            _print_type_details(cache_icon, result)
            CLISettings.console().print(CLISettings.footer_panel())

        except (RuntimeError, OSError, ValueError) as err:
            CLISettings.console().print(f"[danger]Error: {err}[/danger]")
            logger.exception(f"Error getting type {type_id}")
            sys.exit(1)

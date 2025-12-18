"""Types CLI commands."""

import asyncio
import sys
from typing import Any

import click

from rich.table import Table

from numistalib import logger
from numistalib.cli.theme import CLISettings
from numistalib.config import create_async_client_from_settings, create_client_from_settings, get_settings
from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services import TypeBasicService, TypeFullService


# pyright: reportOptionalMemberAccess = false

def _make_table(items: list[Any] | None, title: str | None = None) -> Table | None:
    if not items:
        return None
    table = CLISettings.create_table(title=title)
    # Infer columns from first item
    if items:
        columns = CLISettings.infer_columns_from_model(items[0].__class__)
        CLISettings.add_columns_to_table(table, columns)
        for item in items:
            CLISettings.add_model_row(table, item)
    return table

async def _consume_type_search_results(
    service: TypeBasicService,
    table: Table,
    search_params: dict[str, Any],
) -> int:
    """Consume and display paginated type search results asynchronously.

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
        CLISettings.add_model_row(  # Updated to use the refactored method
            table,
            result,
            cache_indicator=service.last_cache_indicator,
        )
    return count

def _print_type_details(service: TypeFullService, result: TypeFull) -> None:
    """Print detailed type information using theme-aware, vertical scrolling layout."""
    console = CLISettings.console()

    def safe(val: Any, default: str = "") -> str:
        return val if val is not None and str(val).strip() != "" else default

    # === Main Summary Panel ===
    status = "[danger]Demonetized[/danger]" if result.demonetization.is_demonetized else "[success]Current[/success]"

    console.print(
        CLISettings.panel(
            f"""
[header]Type ID:[/header]       [value_highlight]{result.numista_id}[/value_highlight]
[header]Title:[/header]         [value_highlight]{result.title}[/value_highlight]
[header]Years:[/header]         {result.year_range}
[header]Category:[/header]      {result.category.upper()}
[header]Status:[/header]        {status}
[header]Numista URL:[/header]   [link={result.numista_url}]{result.numista_url}[/link]
            """.strip(),
            title=f"{service.last_cache_indicator} Type Details",
            border_style="panel_info",
        )
    )
    

    issuer_panel = CLISettings.panel(
        f"""
[header]Code:[/header]          {result.issuer.code}
[header]Name:[/header]          {result.issuer.name}
[header]Level:[/header]         {result.issuer.level}
[header]Parent:[/header]        {safe(result.issuer.parent_name)}
[header]Wikidata:[/header]      {safe(result.issuer.wikidata_id)}
[header]Flag:[/header]          {safe(result.issuer.flag)}
        """.strip(),
        title="Issuer",
    )

    value_panel = CLISettings.panel(
        f"""
[header]Face Value:[/header]    {safe(result.value.text, "No face value")}
[header]Currency:[/header]      {safe(result.value.currency.full_name)}
[header]Code:[/header]          {safe(result.value.currency.code)}
[header]Symbol:[/header]        {safe(result.value.currency.symbol)}
        """.strip(),
        title="Face Value",
    )

    specs_panel = CLISettings.panel(
        f"""
[header]Diameter:[/header]      {safe(result.size)} mm
[header]Thickness:[/header]     {safe(result.thickness)} mm
[header]Weight:[/header]        {safe(result.weight)} g
[header]Shape:[/header]         {safe(result.shape)}
[header]Composition:[/header]   {safe(result.composition.text)}
[header]Technique:[/header]     {safe(result.technique.text)}
        """.strip(),
        title="Physical Specifications",
    )

    console.print(issuer_panel)
    console.print(value_panel)
    console.print(specs_panel)

    # === Obverse & Reverse ===
    for side, data in [("Obverse", result.obverse), ("Reverse", result.reverse)]:
        if not data:
            continue

        lettering = (
            "\n     ".join([f"{l}" for l in data.lettering.split("\n")])
            if data.lettering
            else ""
        )

        scripts = (
            "\n   ".join([f"• {s.name}" for s in data.lettering_scripts])
            if data.lettering_scripts
            else ""
        )

        console.print(
            CLISettings.panel(
                f"""
[header]Description:[/header]
     {data.description or ''}

[header]Lettering:[/header]
     {lettering}

[header]Scripts:[/header]
   {scripts}

[header]Images:[/header]
   • [link={data.picture}]Full Picture[/link]
   • [link={data.thumbnail}]Thumbnail[/link]
   • [link={data.picture_copyright_url}]{data.picture_copyright or 'Copyright'}[/link]
                """.strip(),
                title=side,
                border_style="panel_info",
            )
        )
        
    if result.rulers:
        rulers_table = _make_table(result.rulers)
        console.print(CLISettings.panel(rulers_table, title="Rulers"))

    if result.mints:
        mints_table = _make_table(result.mints)
        console.print(CLISettings.panel(mints_table, title="Mints"))
    if result.references:
        references_table = _make_table(result.references)
        console.print(CLISettings.panel(references_table, title="Catalogue References" ))
            
    # === Tags & Comments ===
    if result.tags:
        tags_text = "  ".join([f"[tag] {t} [/tag]" for t in result.tags])
        console.print(CLISettings.panel(tags_text, title="Tags"))

    if result.comments:
        console.print(CLISettings.panel(f"[value_dim]{result.comments}[/value_dim]", title="Comments"))

    console.print(CLISettings.panel(CLISettings.LICENSE_TEXT, border_style="footer"))


def register_types_commands(parent: click.Group) -> None:
    """Register types commands with parent group."""

    @parent.group()
    def types() -> None:
        """Search and retrieve coin/banknote/exonumia types."""

    @types.command(name="search")
    @click.option("-q", "--query", help="Full-text search query")
    @click.option("-i", "--issuer", help="Issuer code (e.g., 'united-states')")
    @click.option("-y", "--year", type=int, help="Filter by year")
    @click.option("-c", "--category", type=click.Choice(["coin", "banknote", "exonumia"]), help="Category")
    @click.option("--limit", type=int, default=50, help="Maximum results to return")
    def types_search(
        query: str | None,
        issuer: str | None,
        year: int | None,
        category: str | None,
        limit: int,
    ) -> None:
        """Search the catalogue for types."""
        console = CLISettings.console()

        try:
            settings = get_settings()
            client = create_async_client_from_settings(settings)
            service = TypeBasicService(client)

            table = CLISettings.create_table("Search Results", include_cache_column=True)
            columns = CLISettings.infer_columns_from_model(TypeBasic, include_cache=True)
            CLISettings.add_columns_to_table(table, columns)

            search_params: dict[str, Any] = {
                "query": query,
                "issuer": issuer,
                "year": year,
                "category": category,
                "limit": limit,
            }

            count = asyncio.run(_consume_type_search_results(service, table, search_params))

            if count == 0:
                console.print("[warning]No results found[/warning]")
            else:
                console.print(table)
                console.print(f"\n[success]Displayed {count} result{'s' if count != 1 else ''}[/success]")

        except Exception as err:
            console.print(f"[danger]Error:[/danger] {err}")
            logger.exception("Search failed")
            sys.exit(1)
    @types.command(name="get")
    @click.argument("type_id", type=int)
    def types_get(type_id: int) -> None:
        """Retrieve full details for a specific type by ID."""
        console = CLISettings.console()

        try:
            settings = get_settings()
            client = create_client_from_settings(settings)
            service = TypeFullService(client)
            result = service.get_type(type_id)
            _print_type_details(service, result)
        except Exception as err:
            console.print(f"[danger]Error retrieving type {type_id}:[/danger] {err}")
            logger.exception("Get type failed")
            sys.exit(1)
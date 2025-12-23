"""Types CLI commands."""

import asyncio
from typing import Any

import click
from rich.table import Table
from rich.console import Group

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services import TypeBasicService, TypeFullService

# pyright: reportOptionalMemberAccess = false
# pyright: reportUnknownArgumentType = false
# pyright: reportUnknownMemberType = false

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


def print_type_details(service: TypeFullService, t: TypeFull) -> None:
    """Print detailed type information using theme-aware, vertical scrolling layout."""
    console = CLISettings.console()

    general_panel = CLISettings.panel(
        title=f"{service.last_cache_indicator} Type Details",
        content=f"""
{t.formatted_fields_dict.get("numista_Id")}
{t.formatted_fields_dict.get("numista_url")}
{t.formatted_fields_dict.get("title")}
{t.formatted_fields_dict.get("series")}
{t.formatted_fields_dict.get("category")}
{t.formatted_fields_dict.get("year_range")}
{t.demonetization.formatted_fields_dict.get("is_demonetized",  "")}
{t.formatted_fields_dict.get("commemorated_topic")}

[header]Tags:[/header]
{" ".join([f"[inverse]{g}[/inverse]" for g in t.tags]) if t.tags else ""}
        """)


    value_panel = CLISettings.panel(
        title="Value",
        content=f"""
{t.value.formatted_fields_dict.get("text", "")}
{t.value.formatted_fields_dict.get("numeric_value", "")}
{t.value.formatted_fields_dict.get("numerator", "")}
{t.value.formatted_fields_dict.get("denominator", "")}
[header]Currency:[/header]
{t.value.currency.formatted_fields_dict.get("name", "")}
{t.value.currency.formatted_fields_dict.get("full_name", "")}
{t.value.currency.formatted_fields_dict.get("symbol", "")}
{t.value.currency.formatted_fields_dict.get("numista_id", "")}
""")

    issuer_panel = CLISettings.panel(
        title="Issuer",
        content=f"""
{t.formatted_fields_dict.get("issuing_entity")}
{t.formatted_fields_dict.get("issue_terms")}
{t.issuer.formatted_fields_dict.get("code", "")}
{t.issuer.formatted_fields_dict.get("name", "")}""")
    mints_panel = CLISettings.panel(
        title="Mints",
        content=t.as_table(t.mints, title="Mints") if t.mints else "No mints available")


    specs_panel = CLISettings.panel(
        title="Physical Specifications",
        content= f"""
{t.formatted_fields_dict.get("orientation", "")}
{t.formatted_fields_dict.get("shape", "")}
{t.formatted_fields_dict.get("size", "")}
{t.formatted_fields_dict.get("thickness", "")}
[header]Composition:[/header]
{t.composition.formatted_fields_dict.get("text", "")}
""")

    edge_panel = CLISettings.panel(
        title="Edge Specifications",
        content=Group(
            "\n".join([f for f in t.edge.formatted_fields]) if t.edge else "No edge specifications",
            t.edge.renderable_thumbnail if t.edge and t.edge.renderable_thumbnail else ""
        ) if t.edge else "No edge specifications")
    obverse_panel = CLISettings.panel(
        title="Obverse Specifications",
        content=Group(
            "\n".join([f for f in t.obverse.formatted_fields]),
            t.obverse.renderable_thumbnail if t.obverse.renderable_thumbnail else ""
        ))

    reverse_panel = CLISettings.panel(
        title="Reverse Specifications",
        content=Group(
            "\n".join([f for f in t.reverse.formatted_fields]),
            t.reverse.renderable_thumbnail if t.reverse.renderable_thumbnail else ""
        ))

    rulers_panel = CLISettings.panel(
        title="Rulers",
        content=t.as_table(t.rulers, title="") if t.rulers else "No rulers available")

    references_panel = CLISettings.panel(
        title="References",
        content=t.as_table(t.references, title="") if t.references else "No references available")

    related_types_panel = CLISettings.panel(
        title="Related Types",
        content=t.as_table(t.related_types, title="") if t.related_types else "No related types available")

    comments_panel = CLISettings.panel(
        title="Comments",
        content=t.formatted_fields_dict.get("comments", "")
    )

    console.print(general_panel)
    console.print(value_panel)
    console.print(issuer_panel)
    console.print(mints_panel)
    console.print(specs_panel)
    console.print(edge_panel)
    console.print(obverse_panel)
    console.print(reverse_panel)
    console.print(rulers_panel)
    console.print(references_panel)
    console.print(related_types_panel)
    console.print(comments_panel)
    console.print(CLISettings.LICENSE_TEXT, style="footer")


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
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def types_search(
        query: str | None,
        issuer: str | None,
        year: int | None,
        category: str | None,
        limit: int,
        lang: str,
    ) -> None:
        """Search the catalogue for types."""
        console = CLISettings.console()
        settings = Settings()
        client = Settings.to_async_client(settings)
        service = TypeBasicService(client)

        try:
            # settings already created above

            table = CLISettings.create_table("Search Results", include_cache_column=True)
            columns = CLISettings.infer_columns_from_model(TypeBasic, include_cache=True)
            CLISettings.add_columns_to_table(table, columns)

            search_params: dict[str, Any] = {
                "query": query,
                "issuer": issuer,
                "year": year,
                "category": category,
                "limit": limit,
                "lang": lang,
            }

            count = asyncio.run(_consume_type_search_results(service, table, search_params))

            if count == 0:
                console.print("[warning]No results found[/warning]")
            else:
                console.print(table)
                console.print(f"\n[success]Displayed {count} result{'s' if count != 1 else ''}[/success]")

        except Exception as err:
            service.handle_cli_error(err, "searching types", "types-search")

    @types.command(name="get")
    @click.argument("type_id", type=int)
    @click.option("--lang", default="en", type=click.Choice(["en", "es", "fr"]), help="Language")
    def types_get(type_id: int, lang: str) -> None:
        """Retrieve full details for a specific type by ID."""
        CLISettings.console()
        settings = Settings()
        client = Settings.to_client(settings)
        service = TypeFullService(client)
        try:

            result = service.get_type(type_id, lang=lang)
            print_type_details(service, result)
        except Exception as err:
            service.handle_cli_error(err, f"retrieving type {type_id}", "types-get")

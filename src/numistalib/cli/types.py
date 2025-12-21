"""Types CLI commands."""

import asyncio
from typing import Any

import click
from bs4 import BeautifulSoup
from rich.console import Group
from rich.table import Table
from rich.text import Text

from numistalib.cli.theme import CLISettings
from numistalib.config import Settings
from numistalib.models.types import TypeBasic, TypeFull
from numistalib.services import TypeBasicService, TypeFullService

# pyright: reportOptionalMemberAccess = false



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


def print_type_details(service: TypeFullService, type_full: TypeFull) -> None:
    """Print detailed type information using theme-aware, vertical scrolling layout."""
    console = CLISettings.console()
    formatted_fields: dict[str, str] = type_full.formatted_fields_dict
    summary_fields = ["numista_id", "title", "year_range", "category", "numista_url"]
    value_fields = ["currency", "value", "unit"]
    specs_fields = ["size", "thickness", "weight", "shape", "composition", "technique"] 


    console.print(CLISettings.panel(
            "\n".join(formatted_fields[field] for field in summary_fields),
            title=f"{service.last_cache_indicator} Type Details",
            border_style="panel_info",
        ))

    console.print(
        CLISettings.panel(
            "\n".join(formatted_fields[field] for field in value_fields),
            title="Face Value"
        )
    )

    console.print(
        CLISettings.panel(
            "\n".join(formatted_fields[field] for field in specs_fields),
            title="Physical Specifications"
        )
    )


    # console.print(
    #     CLISettings.panel(
    #         type_full.obverse.panel_template,
    #         title="Obverse Specifications",
    #     )
    # )

    # console.print(
    #     CLISettings.panel(
    #         type_full.reverse.panel_template,
    #         title="Reverse Specifications",
    #     )
    # )

    # console.print(
    #     CLISettings.panel(
    #         formatted_fields["issuers"],
    #         title="Issuing Entities",
    #     )
    # )


    # # === Optional Panels ===
    # if type_full.rulers:
    #     rulers_table = type_full.rulers[0].__class__.as_table(type_full.rulers, title="Rulers")
    #     console.print(CLISettings.panel(rulers_table, title="Rulers"))

    # if type_full.comments:
    #     converted = _html_to_rich_markup(type_full.comments)
    #     comments_text = Text.from_markup(
    #         f"[value_dim]{converted}[/value_dim]",
    #         overflow="fold",
    #     )
    #     comments_text.no_wrap = False
    #     console.print(
    #         CLISettings.panel(
    #             comments_text,
    #             title="Comments",
    #             expand=True,
    #         )
    #     )

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

        try:
            settings = Settings()
            client = Settings.to_client(settings)
            service = TypeFullService(client)
            result = service.get_type(type_id, lang=lang)
            print_type_details(service, result)
        except Exception as err:
            service.handle_cli_error(err, f"retrieving type {type_id}", "types-get")

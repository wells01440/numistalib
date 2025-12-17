"""Types CLI commands."""

import asyncio
from operator import add
from os import name
import re
import sys
from typing import Any

import click
from pydantic import Field
from rich import console, print
from rich import layout
from rich import columns
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.columns import Columns
from rich.pretty import Pretty

from numistalib import logger
from numistalib.cli.theme import CLISettings
from numistalib.config import create_async_client_from_settings, create_client_from_settings, get_settings
from numistalib.models.types import TypeFull
from numistalib.services import TypeBasicService, TypeFullService

from pydantic import Field


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



# type: ignore
def _pydantic_to_rich_table(field: Any) -> Table:
    """Convert Pydantic Field of list type to Rich Table.

    Parameters
    ----------
    field : Any
        Pydantic Field representing a list of items

    Returns
    -------
    Table
        Rich Table representation of the field's items
    """
    field_name = field[0].__class__.__name__

    table = Table(
        show_header=True, 
        show_lines=False,
        show_edge=False,
        expand=True,
        header_style="header",
        title="",
        title_justify="left",
        caption=f"Total: {len(field)}", 
        caption_justify="right")  

    columns = [c for c in field[0].model_fields] + [c for c in field[0].model_computed_fields]
    for c in columns:
        table.add_column(c.upper())

    for r in field:
        row_vals = []
        for c in columns:
            v = getattr(r, c)
            row_vals.append(str(v) if v is not None else "")
        table.add_row(*row_vals)

    logger.debug("Constructed table for field: %s", field_name)
    return table

        

def _print_type_details(cache_icon: str, result: TypeFull) -> None:
    """Print detailed type information.

    Parameters
    ----------
    cache_icon : str
        Cache indicator icon
    result : TypeFull
        Full type result object
    """
    console = CLISettings.console()
    console.print(f"\n{cache_icon} [header]Type ID:[/header] {result.id}")
    console.print(f"[header]Title:[/header] {result.title}")
    console.print(f"{result.to_dict()}\n")

    rulers_table = _pydantic_to_rich_table(result.rulers)
    mints_table = _pydantic_to_rich_table(result.mints)
    references_table = _pydantic_to_rich_table(result.references)


    summary_panel = Panel(f"""
[header]Type ID:[/header]    {result.id}
[header]Title:[/header]      {result.title}
[header]Years:[/header]      {result.min_year}-{result.max_year}  ({'demonitized' if result.demonetization and result.demonetization.is_demonetized else 'active'})
[header]Type:[/header]       {result.type}
[header]Category:[/header]   {result.category}
[header]Comments:[/header]   [italic]{result.comments}[/italic]
[header]Tags:[/header]   
    {' '.join([f"[reverse]{t}[/reverse]" for t in result.tags ]) if result.tags else ''}
    """, title=f"{cache_icon} Type Summary", title_align="left")

    issue_panel = Panel(f"""
[header]Issuer Code:[/header]      {result.issuer.code}
[header]Issuer Name:[/header]      {result.issuer.name}
[header]Issuer Level:[/header]     {result.issuer.level}
[header]wikidata_id:[/header]      {result.issuer.wikidata_id}
[header]Flag URL:[/header]         {result.issuer.flag}
[header]Parent Code:[/header]      {result.issuer.parent_code}
[header]Parent Name:[/header]      {result.issuer.parent_name}
         """, title="Issuer Details", title_align="left")
    
    currency_panel = Panel(f"""
[header]Value:[/header]   {result.value.numeric_value} / ({result.value.text}) {result.value.currency.symbol if result.value.currency.symbol else ''}
[header]ID:[/header]      {result.value.currency.numista_id}
[header]Code:[/header]    {result.value.currency.code}
[header]Name:[/header]    {result.value.currency.full_name}
[header]Symbol:[/header]  {result.value.currency.symbol}
    """, title="Currency Details", title_align="left") 

    attributes_panel = Panel(f"""
[header]Size (mm):[/header]        {result.size}
[header]Shape:[/header]            {result.shape}
[header]Composition:[/header]      {result.composition.text}
[header]Technique:[/header]        {result.technique.text}
[header]Weight (g):[/header]       {result.weight}
[header]Edge:[/header]             {', '.join([e for e in result.edge.values()]) if result.edge else ''}
    """, title="Physical Attributes", title_align="left")

    obverse_panel = Panel(f"""
[header]Description:[/header]      {result.obverse.description}
[header]View[/header] 
    [link={result.obverse.picture}]Picture[/link] 
    [link={result.obverse.thumbnail}]Thumbnail[/link]
    [link={result.obverse.picture_copyright_url}]{result.obverse.picture_copyright}[/link]
[header]Lettering Script(s):[/header]
     [bold]{'\n    '.join([script.name for script in result.obverse.lettering_scripts])}[/bold]
[header]Lettering:[/header]           
     { '\n     '.join(result.obverse.lettering.split('\n')) }
    """, title="Obverse Details", title_align="left")

    reverse_panel = Panel(f"""
[header]Description:[/header]     {result.reverse.description}
[header]View[/header] 
    [link={result.reverse.picture}]Picture[/link] 
    [link={result.reverse.thumbnail}]Thumbnail[/link]
    [link={result.reverse.picture_copyright_url}][:copyright:]{result.reverse.picture_copyright}[/link]
[header]Lettering Scripts:[/header] 
     [bold]{'\n    '.join([script.name for script in result.reverse.lettering_scripts])}[/bold]
[header]Lettering:[/header]         
     { '\n     '.join(result.reverse.lettering.split('\n')) }

    """, title="Reverse Details", title_align="left")

    layout = Layout()
    layout.split_column(
        Layout(name="top", minimum_size=11),
        Layout(name="middle", minimum_size=14),
        Layout(name="bottom", minimum_size=8)
    )

    layout["top"].split_row(
                    Layout(name="tl", ratio=2, renderable=summary_panel),
                    Layout(name="tm", renderable=issue_panel),
                    Layout(name="tr", renderable=currency_panel),
                    Layout(name="trr", renderable=attributes_panel)
    )

    layout["middle"].split_row(
        Layout(name="ml", ratio=2, renderable=obverse_panel),
        Layout(name="mr", ratio=2, renderable=reverse_panel),
    )

    layout["bottom"].split_row(
        Layout(name="bl", renderable=Panel(rulers_table, title="Rulers", title_align="left")),
        Layout(name="bm", renderable=Panel(mints_table, title="Mints", title_align="left")),
        Layout(name="br", renderable=Panel(references_table, title="References"))
    )
    console.print(layout)





# ╭─────────────────────╮
# │ Type Details: 95420 │
# ╰─────────────────────╯

# 💾 Type ID: 95420
# Title: 1 Conventionsthaler
# {'id': 95420, 'url': Url('https://en.numista.com/95420'), 'title': '1 Conventionsthaler', 'category': 'coin', 'issuer': {'code': 'muhlhausen_free_imperial_city', 'name': 'Mühlhausen, Free imperial city of'}, 'min_year': 1767,
# 'max_year': 1767, 'type': 'Standard circulation coins', 'rulers': [{'id': 6176, 'name': 'Free city', 'wikidata_id': 'Q14925'}, {'id': 8536, 'name': 'Joseph II', 'wikidata_id': 'Q76555', 'group': {'id': 867, 'name': 'Emperors 
# of the Holy Roman Empire'}}], 'value': {'text': '1 Thaler', 'numeric_value': 1.0, 'currency': {'numista_id': 6357, 'full_name': 'Thaler'}}, 'demonetization': {'is_demonetized': True}, 'size': 40.0, 'shape': 'Round', 
# 'composition': {'text': 'Silver'}, 'technique': {'text': 'Milled'}, 'obverse': {'description': 'Helmeted arms, legend surrounding.', 'lettering': 'X. EINE FEINE MARCK.\r\nCIVIT.IMPERIALIS MULHUSINÆ.1767', 'lettering_scripts':
# [{'name': 'Latin'}], 'picture': Url('https://en.numista.com/catalogue/photos/muhlhausen_free_imperial_city/63ee272fcae564.11703305-original.jpg'), 'thumbnail': 
# Url('https://en.numista.com/catalogue/photos/muhlhausen_free_imperial_city/63ee272fcae564.11703305-180.jpg'), 'picture_copyright': 'Heritage Auctions', 'picture_copyright_url': Url('http://www.ha.com/')}, 'reverse': 
# {'description': 'Laureate and armored bust facing right.', 'lettering': 'COR.&HER.R.H.B.&C. IOSEPH.II.D.G.R.I.S.A.', 'lettering_scripts': [{'name': 'Latin'}], 'picture': 
# Url('https://en.numista.com/catalogue/photos/muhlhausen_free_imperial_city/63ee27316db429.97721947-original.jpg'), 'thumbnail': 
# Url('https://en.numista.com/catalogue/photos/muhlhausen_free_imperial_city/63ee27316db429.97721947-180.jpg'), 'picture_copyright': 'Heritage Auctions', 'picture_copyright_url': Url('http://www.ha.com/')}, 'references': 
# [{'catalogue': 'KM', 'number': '75'}, {'catalogue': 'Dav GT II', 'number': '2462'}], 'mints': [{'numista_id': 230, 'name': 'Clausthal'}]}

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
            numistalib types search -q "dollar"
            numistalib types search --issuer united-states --year 2020
            numistalib types search -q "thaler" --category coin
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
            numistalib types get 95420
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

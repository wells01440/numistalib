"""Rich v14 theming and formatting utilities for numistalib CLI.

Provides consistent theming, console access, table helpers, and panel formatting
in line with AGENTS.md § 7.1 requirements.
"""

from __future__ import annotations

from sys import version_info
from typing import Any, Iterable

from pydantic import BaseModel
from rich import box
from rich.align import AlignMethod
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from numistalib import  __version__

# pyright: reportOptionalMemberAccess = false, reportUnknownMemberType = false

class CLISettings:
    """Centralized CLI styling and formatting utilities."""

    # === Constants ===
    CLI_THEME: dict[str, str] = {
        # === Feedback / Status Messages ===
        "info": "bright_cyan",          # General informational text
        "success": "bold bright_green", # Success states, confirmations
        "warning": "bold bright_yellow",# Warnings, deprecations
        "danger": "bold bright_red",    # Errors, critical issues
        "error": "bright_red",          # Slightly softer errors (e.g., validation)
        "debug": "dim magenta",         # Debug/log output

        # === Headers & Structural Elements ===
        "header": "bold bright_blue",   # Section titles, field labels
        "subheader": "bold cyan",       # Secondary headers
        "footer": "dim white",          # Copyright, status lines

        # === Data Presentation ===
        "key": "bold white",            # Field names / keys in detail views
        "value": "white",               # Regular values
        "value_highlight": "bold bright_cyan",  # Important values (e.g., title, ID)
        "value_dim": "dim white",       # Less important metadata
        "value_missing": "dim italic",  # "—" or "None" placeholders

        # === Tables & Lists ===
        "table_header": "bold bright_blue on grey15",  # Table column headers
        "row_data": "white",            # Regular data rows
        "row_even": "white",            # Even rows
        "row_odd": "bright_white",      # Odd rows (slight contrast)
        "row_emphasized": "bold bright_cyan",  # Highlighted rows/cells
        "row_metadata": "dim white",    # Secondary info in tables

        # === Tags & Badges ===
        "tag": "reverse black on bright_white",     # General tags
        "tag_coin": "reverse black on bright_yellow",   # Category-specific if desired
        "tag_banknote": "reverse black on bright_green",
        "tag_exonumia": "reverse black on bright_magenta",

        # === Links & Interactive ===
        "link": "underline bright_cyan",   # Hyperlinks
        "link_hover": "bold underline bright_cyan",

        # === Specific Numista Semantics ===
        "demonetized": "bold red",         # Demonetized status
        "current_currency": "bold green",  # Still legal tender
        "cache_hit": "dim green",          # ♻ Cached indicator
        "cache_miss": "dim yellow",        # Fresh fetch indicator

        # === Panel Borders (optional overrides) ===
        "panel_info": "bright_cyan",
        "panel_success": "bright_green",
        "panel_warning": "bright_yellow",
        "panel_danger": "bright_red",
        "panel_default": "bright_blue",
    }

    LICENSE_TEXT: str = "MIT License - See LICENSE file for details"
    PANEL_WIDTH: int = 120
    VERSION: str = __version__
    PANEL_BOX_STYLE: box.Box = box.ROUNDED
    PADDING_DIMENSIONS: tuple[int, int] = (1, 1)
    PANEL_EXPAND: bool = True
    PANEL_TITLE_ALIGN: AlignMethod = "left"
    PANEL_HIGHLIGHT: bool = True
    TABLE_BOX_STYLE: box.Box = box.SIMPLE
    TABLE_EXPAND: bool = True
    TABLE_HIGHLIGHT: bool = True
    TABLE_SHOW_TITLE: bool = False
    TABLE_SHOW_HEADER: bool = True

    # === Cached Rich Objects (lazy initialization) ===
    _console: Console | None = None
    _theme: Theme | None = None

    # === Public Accessors ===
    @classmethod
    def theme(cls) -> Theme:
        """Return the configured CLI theme (cached)."""
        if cls._theme is None:
            cls._theme = Theme(cls.CLI_THEME)
        return cls._theme

    @classmethod
    def console(cls) -> Console:
        """Return a Console instance with CLI theme applied (cached singleton)."""
        if cls._console is None:
            cls._console = Console(
                theme=cls.theme(),
                markup=True,
                highlight=False,
                width=cls.PANEL_WIDTH,
                soft_wrap=True,
            )
        return cls._console

    @classmethod
    def version_info(cls) -> str:
        """Return formatted version string."""
        return f"numistalib CLI v{cls.VERSION} (Python {version_info.major}.{version_info.minor}.{version_info.micro})"

    # === Table Helpers ===
    @classmethod
    def create_table(
        cls,
        title: str | None = None,
        include_cache_column: bool = False,
    ) -> Table:
        """Create a consistently styled table."""
        table = Table(
            title=title,
            show_header=cls.TABLE_SHOW_HEADER,
            header_style="table_header",
            title_justify="left",
            row_styles=["row_even", "row_odd"],
            expand=True,
            box=cls.TABLE_BOX_STYLE,
        )
        if include_cache_column:
            table.add_column("Cache", style="row_metadata", no_wrap=True, width=6)

        return table

    @classmethod
    def infer_columns_from_model(
        cls,
        model_cls: type[BaseModel],
        include_cache: bool = False,
    ) -> list[str]:
        """Infer human-readable column names from a Pydantic model."""
        columns: list[str] = []

        if include_cache:
            columns.append("Cache")

        # Use model_fields for reliable ordering and metadata
        for field_name, field_info in model_cls.model_fields.items():
            # Prefer description if available, else title-cased name
            column_name = field_info.description or field_name.replace("_", " ").title()
            columns.append(column_name)

        return columns

    @classmethod
    def add_columns_to_table(
        cls,
        table: Table,
        columns: Iterable[str],
    ) -> None:
        """Add columns with appropriate styling based on semantic meaning."""
        for column in columns:
            if column == "Cache":
                style = "row_metadata"
                no_wrap = True
            elif column in {"ID", "Id", "Numista ID", "Numista Id", "Code"}:
                style = "row_data_emphasized"
                no_wrap = True
            else:
                style = "row_data"
                no_wrap = False

            table.add_column(column, style=style, no_wrap=no_wrap)

    @classmethod
    def add_model_row(
        cls,
        table: Table,
        model_instance: BaseModel,
        cache_indicator: str = "",
    ) -> None:
        """Add a row from a Pydantic model instance, respecting column order."""
        values: list[str] = []

        # Determine if first column is cache
        has_cache_column = table.columns and table.columns[0].header == "Cache"
        if has_cache_column:
            values.append(cache_indicator)

        # Add values in model_fields order (consistent with inferred columns)
        for field_name in type(model_instance).model_fields:
            if field_name in model_instance.model_fields_set or getattr(model_instance, field_name) is not None:
                value = getattr(model_instance, field_name)
                values.append(str(value) if value is not None else "")

        table.add_row(*values)

    # === Convenience Panel Helpers ===
    # pyright
    @classmethod
    def panel(
        cls,
        content: str | Any,
        box: box.Box | None = None,
        title: str | None = None,
        padding: tuple[int, int] | None = None,
        width: int | None = None,
        expand: bool = True,
        title_align: AlignMethod | None = None,
        **kwargs: Any,
    ) -> Panel:
        """Create a consistently styled Panel."""
        return Panel(
            content,
            title=title,
            box=box if box else cls.PANEL_BOX_STYLE,
            expand=expand if expand else cls.PANEL_EXPAND,
            width=width if width else cls.PANEL_WIDTH ,
            padding=padding if padding else cls.PADDING_DIMENSIONS,
            title_align=title_align if title_align else cls.PANEL_TITLE_ALIGN,
            **kwargs,
        )
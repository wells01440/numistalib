"""Rich v14 theming and formatting utilities for numista-lib CLI.

Provides consistent theming, headers, footers, and panel formatting
per AGENTS.md § 7.1 requirements.
"""

from sys import version
from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from numista_lib import CLI_LICENSE_TEXT, CLI_PANEL_WIDTH, CLI_THEME, __version__


class CLISettings:
    """CLI settings for theming and formatting."""
    panel_width = CLI_PANEL_WIDTH
    license_text = CLI_LICENSE_TEXT
    version = __version__
    theme_dict = CLI_THEME

    @staticmethod
    def footer_panel() -> Panel:
        """Get footer text with version and license info."""
        return Panel(
            f"{CLISettings.license_text} | {CLISettings.version_info()}",
            style="footer",
            width=CLISettings.panel_width,
            expand=False,
        )

    @staticmethod
    def header_panel(title: str) -> Panel:
        """Get header text with title."""
        return Panel(
            title,
            style="header",
            width=CLISettings.panel_width,
            expand=False,
        )

    @staticmethod
    def theme() -> Theme:
        """Get CLI theme."""
        return Theme(CLISettings.theme_dict)

    @staticmethod
    def version_info() -> str:
        """Get version info string."""
        return f"numista-lib CLI v{CLISettings.version} (Python {version.split()[0]})"

    @staticmethod
    def table_from_model_class(
        model_cls: type[BaseModel],
        include_cache: bool = True,
        title: str | None = None,
    ) -> Table:
        """Create a table with columns based on Pydantic model class.

        Parameters
        ----------
        model_cls : type[BaseModel]
            Pydantic model class to introspect
        include_cache : bool, optional
            Whether to include a "Cache" column, by default True
        title : str | None, optional
            Table title, defaults to model name + " Results"

        Returns
        -------
        Table
            Configured table with inferred columns
        """
        title = title or f"{model_cls.__name__} Results"
        table = Table(
            title=title,
            show_header=True,
            header_style="header",
            width=CLISettings.panel_width,
        )

        columns: list[str] = []
        if include_cache:
            columns.append("Cache")

        # Infer columns from Pydantic model schema
        schema = model_cls.model_json_schema()
        properties = schema.get("properties", {})

        for field_name in properties.keys():
            column_name = field_name.replace("_", " ").title()
            columns.append(column_name)

        CLISettings.table_add_columns(table, columns)
        return table

    @staticmethod
    def create_table(title: str) -> Table:
        """Create a consistently styled table.

        Parameters
        ----------
        title : str
            Table title

        Returns
        -------
        Table
            Configured table with standard styling
        """
        return Table(
            title=title,
            show_header=True,
            header_style="header",
            width=CLISettings.panel_width,
        )

    @staticmethod
    def table_add_columns(
        table: Table,
        columns: list[str],
    ) -> None:
        """Add columns to a table with consistent styling.

        Parameters
        ----------
        table : Table
            Table to add columns to
        columns : list[str]
            List of column names
        """
        for column_name in columns:
            if column_name == "Cache":
                table.add_column(column_name, style="row_metadata", no_wrap=True)
            elif column_name in {"ID", "Id", "Code", "Numista Id"}:
                table.add_column(column_name, style="row_data_emphasized", no_wrap=True)
            else:
                table.add_column(column_name, style="row_data")

    @staticmethod
    def table_add_row(
        table: Table,
        values: list[Any],
    ) -> None:
        """Add a row to a table with consistent formatting.

        Parameters
        ----------
        values : list[Any]
            Column values for the row
        """
        table.add_row(*[str(value) for value in values])

    @staticmethod
    def table_add_model_row(
        table: Table,
        model_instance: BaseModel,
        include_cache: bool = True,
        cache_icon: str = "",
    ) -> None:
        """Add a row to a table from a Pydantic model instance.

        Parameters
        ----------
        table : Table
            Table to add row to
        model_instance : BaseModel
            Pydantic model instance to extract values from
        include_cache : bool, optional
            Whether to include a "Cache" column, by default True
        cache_icon : str, optional
            Cache icon to use if including cache column, by default ""
        """
        values: list[Any] = []
        if include_cache:
            values.append(cache_icon)

        for field in model_instance.model_fields_set:
            value = getattr(model_instance, field)
            values.append(value)

        CLISettings.table_add_row(table, values)

    @staticmethod
    def console() -> Console:
        """Get console with CLI theming."""
        return Console(theme=CLISettings.theme())

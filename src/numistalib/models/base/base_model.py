"""Base models for all Numista entities.

Common configuration, behavior, and abstract base classes for Pydantic models.
"""
import re
from abc import ABC
from typing import Any

import rich.repr
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from rich.table import Table

# Panel formatting constants
PANEL_VALUE_COLUMN: int = 20
PANEL_HANGING_INDENT: int = 5


def safe(val: Any, default: str = "") -> str:
        """Return string representation or default if None or empty."""
        return val if val is not None and str(val).strip() else default


def scrub(value: Any) -> str:
    """Scrub HTML from field values, preserving formatting.

    Uses BeautifulSoup4 to detect paragraphs, breaks, and links,
    converting them to appropriate plain text with Rich markup.

    Parameters
    ----------
    value : Any
        Field value (may contain HTML)

    Returns
    -------
    str
        Cleaned value with Rich markup for links
    """
    text = safe(value)

    if not type(text) == str:
        return str(text)

    # Check if value contains HTML
    if ("<" in text and ">" in text):
        soup = BeautifulSoup(text, "html.parser")

        # Convert paragraphs to double newlines
        for p in soup.find_all("p"):
            p.replace_with(f"{p.get_text(strip=False)}\n")

        # Convert breaks to single newlines
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # Fix links - convert to Rich markup
        for link in soup.find_all("a"):
            href = link.get("href", "")
            link_text = link.get_text()
            if href:
                link.replace_with(f"[link={href}]{link_text}[/link]")
            else:
                link.replace_with(link_text)

        # Get cleaned text
        text = soup.get_text()

    if text:
        # clean up whitespace
        text = re.sub(r"\n\n\n+", "\n\n", text.strip())  # collapse multiple newlines
        text = re.sub(r"[ \t]+", " ", text)

        # look for line feeds
        cleaned_lines = [l.strip() for l in text.split("\n")]
        text = "\n".join(cleaned_lines)

    return text.strip()


def format_field(
        label: str,
        value: Any,
        value_column: int | None = None,
        hanging_indent: int | None = None,
        short_line_field_separator: str = " "
    ) -> str:
    """Format a single field with label and value using Rich markup.

    Applies intelligent formatting based on value length and content:
    - Short values (≤25 chars): Same line, aligned at value_column
    - Long values (>25 chars): Next line at column 1
    - Multiline values: Indented at 'indent' columns, extra linefeed after

    Parameters
    ----------
    label : str
        Field label
    value : Any
        Field value
    value_column : int | None
        Column where values start (default: uses panel_value_column class property)
    indent : int | None
        Indentation for multiline values (default: uses hanging_indent class property)

    Returns
    -------
    str
        Formatted field string with Rich markup and proper alignment
    """
    # Use class properties as defaults
    value_column = value_column if value_column is not None else PANEL_VALUE_COLUMN
    hanging_indent = hanging_indent if hanging_indent is not None else PANEL_HANGING_INDENT

    # Scrub HTML and get cleaned value
    cleaned_value = scrub(value)

    # Format label with Rich markup
    formatted_label = f"[label]{label}:[/label]"

    # Detect multiline content
    is_multiline = "\n" in cleaned_value
    value_length = len(cleaned_value.split("\n")[0]) if is_multiline else len(cleaned_value)

    if is_multiline:
        # Multiline: indent each line, add extra linefeed at end
        lines = cleaned_value.split("\n")
        indent_str = " " * hanging_indent
        indented_lines = [f"{indent_str}{line}" for line in lines]
        formatted_value = "\n".join(indented_lines)
        return f"{formatted_label}\n{formatted_value}\n"

    elif value_length > 25:
        # Long single-line: start on next line at column 1, add extra linefeed
        return f"{formatted_label}\n{cleaned_value}\n"

    else:
        # Short value: same line, aligned at value_column
        # Calculate padding to align value at value_column
        label_width = len(label) + 1  # +1 for the colon
        padding_needed = max(1, value_column - label_width)
        padding = short_line_field_separator * padding_needed
        return f"{formatted_label}{padding}[value]{cleaned_value}[/value]"


class NumistaBaseModel(ABC, BaseModel):
    """Base model for all Numista entities.

    Provides a shared Pydantic base configuration with:
    - Strict validation
    - Immutability control
    - Extra field prohibition
    - Consistent configuration
    """

    model_config = ConfigDict(
        strict=True,
        frozen=False,
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=False,
        populate_by_name=True,
        alias_generator=to_camel,
        use_enum_values=True,
    )

    def __rich_repr__(self) -> rich.repr.Result:
        """Make models look good when printed with rich.print()."""
        for name, field in self.__class__.model_fields.items():
            value = getattr(self, name)
            if value is None:  # Skip None fields for cleaner output
                continue
            if field.alias:
                yield field.alias, value
            else:
                yield name, value

    def to_api_dict(self, **kwargs: Any) -> dict[Any, Any]:
        """Return dict suitable for sending back to API or clean export.
        Uses aliases, excludes None by default.
        """
        return self.model_dump(
            by_alias=kwargs.get("by_alias", True),
            exclude_none=kwargs.get("exclude_none", True),
            exclude_unset=kwargs.get("exclude_unset", True),
            **kwargs,
        )

    @property
    def formatted_fields_dict(self) -> dict[str, str]:
        """Return dictionary of formatted strings for all model fields.

        Automatically formats all fields (regular and computed) in the model
        using format_field() with default column alignment and indentation.

        Returns
        -------
        dict[str, str]
            Dictionary mapping field names to formatted field strings
        """
        formatted: dict[str, str] = {}

        # Get all model fields including computed fields
        for field_name in self.__class__.model_fields.keys():
            value = getattr(self, field_name, None)
            if value is not None:  # Skip None values
                # Convert field name to human-readable label
                label = field_name.replace("_", " ").title()
                formatted[field_name] = format_field(label, value)

        # Also include computed fields
        for field_name in self.__class__.model_computed_fields.keys():
            if field_name in ("panel_template", "formatted_fields_dict"):
                continue  # Skip these special fields
            value = getattr(self, field_name, None)
            if value is not None:
                label = field_name.replace("_", " ").title()
                formatted[field_name] = format_field(label, value)

        return formatted

    @property
    def formatted_fields(self) -> list[str]:
        """Return list of formatted strings for all model fields.

        Automatically formats all fields (regular and computed) in the model
        using format_field() with default column alignment and indentation.

        Returns
        -------
        list[str]
            List of formatted field strings
        """
        return list(self.formatted_fields_dict.values())

    def formatted_fields_deep(self) -> dict[str, str]:
        """Return formatted fields and recurse into related model lists without tables."""
        formatted: dict[str, str] = {}

        def process_field(field_name: str, value: Any) -> None:
            if value is None:
                return

            label = field_name.replace("_", " ").title()

            if isinstance(value, list) and value and all(isinstance(item, NumistaBaseModel) for item in value):
                item_blocks = ["\n".join(item.formatted_fields) for item in value]
                formatted[field_name] = format_field(label, "\n\n".join(item_blocks))
                return

            formatted[field_name] = format_field(label, value)

        for field_name in self.__class__.model_fields.keys():
            process_field(field_name, getattr(self, field_name, None))

        for field_name in self.__class__.model_computed_fields.keys():
            if field_name in ("panel_template", "formatted_fields_dict", "formatted_fields_deep"):
                continue
            process_field(field_name, getattr(self, field_name, None))

        return formatted

    @staticmethod
    def as_table(items: list[Any], title: str = "") -> Table:
        """Return a Rich Table representation of model instances.

        Generates a standard table with headers and rows using model field names.

        Parameters
        ----------
        items : list[Any]
            List of model instances to display
        title : str
            Table title

        Returns
        -------
        rich.table.Table
            Rich Table object with headers and data rows
        """
        if not items:
            return Table(title=title)

        # Get all field names from the first item
        all_cols: list[str] = list(items[0].__class__.model_fields.keys())

        # Create table with headers
        table = Table(show_header=True, box=None, pad_edge=False, title=title)
        for col in all_cols:
            # Convert field name to human-readable header
            header = col.replace("_", " ").title()
            table.add_column(header, no_wrap=True)

        # Add rows with simple string values
        for row in items:
            row_values = [str(getattr(row, col, "")) for col in all_cols]
            table.add_row(*row_values)

        return table

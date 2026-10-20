"""KeyValue and Table widgets - structured data display."""

from typing import Dict, List, Any, Optional
from cryptolab.ui.theme import Color, Symbol, Spacing, Width, clip_text, term_width


class KeyValue:
    """Key-value pair display widget."""

    @staticmethod
    def format(key: str, value: Any, key_width: int = 20) -> str:
        """Format a single key-value pair."""
        k = Color.cyan(key.ljust(key_width))
        v = Color.white(str(value))
        return f"{Spacing.INDENT}{k}: {v}"

    @staticmethod
    def render(pairs: Dict[str, Any], key_width: int = 20) -> str:
        """Render multiple key-value pairs."""
        if not pairs:
            return ""
        lines = [KeyValue.format(k, v, key_width) for k, v in pairs.items()]
        return "\n".join(lines)

    @staticmethod
    def print(pairs: Dict[str, Any], key_width: int = 20) -> None:
        """Print key-value pairs to stdout."""
        print(KeyValue.render(pairs, key_width))


class Table:
    """Simple table rendering widget."""

    def __init__(self, headers: List[str], col_widths: Optional[List[int]] = None):
        self.headers = headers
        self.col_widths = col_widths or [Width.DEFAULT // len(headers)] * len(headers)
        self.rows: List[List[str]] = []

    def add_row(self, cells: List[str]) -> "Table":
        """Add a row to the table."""
        # Pad or truncate cells to match column count
        padded = list(cells) + [""] * (len(self.headers) - len(cells))
        self.rows.append(padded[: len(self.headers)])
        return self

    def add_rows(self, rows: List[List[str]]) -> "Table":
        """Add multiple rows."""
        for row in rows:
            self.add_row(row)
        return self

    def _format_cell(self, text: str, width: int, align: str = "left") -> str:
        """Format cell text with alignment and clipping."""
        text = clip_text(str(text), width)
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        return text.ljust(width)

    def render(self, alignments: Optional[List[str]] = None) -> str:
        """Render table as string."""
        if not self.headers:
            return ""

        aligns = alignments or ["left"] * len(self.headers)
        sep = f" {Color.dim(Symbol.BOX_V)} "

        # Header
        header_cells = [
            self._format_cell(h, w, aligns[i]) for i, (h, w) in enumerate(zip(self.headers, self.col_widths))
        ]
        header_line = f"{Color.dim(Symbol.BOX_V)}{sep.join(header_cells)}{Color.dim(Symbol.BOX_V)}"

        # Separator
        sep_line = (
            f"{Color.dim(Symbol.BOX_L)}"
            + f"{Color.dim(Symbol.BOX_X)}".join(Color.dim(Symbol.BOX_H * w) for w in self.col_widths)
            + f"{Color.dim(Symbol.BOX_R)}"
        )

        # Rows
        row_lines = []
        for row in self.rows:
            row_cells = [
                self._format_cell(c, w, aligns[i]) for i, (c, w) in enumerate(zip(row, self.col_widths))
            ]
            row_lines.append(f"{Color.dim(Symbol.BOX_V)}{sep.join(row_cells)}{Color.dim(Symbol.BOX_V)}")

        # Bottom
        bottom_line = (
            f"{Color.dim(Symbol.BOX_BL)}"
            + f"{Color.dim(Symbol.BOX_X)}".join(Color.dim(Symbol.BOX_H * w) for w in self.col_widths)
            + f"{Color.dim(Symbol.BOX_BR)}"
        )

        parts = [header_line, sep_line] + row_lines + [bottom_line]
        return "\n".join(parts)

    @staticmethod
    def render_simple(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None) -> str:
        """Quick static table render."""
        t = Table(headers, col_widths)
        t.add_rows(rows)
        return t.render()

    def print(self, alignments: Optional[List[str]] = None) -> None:
        """Print table to stdout."""
        print(self.render(alignments))
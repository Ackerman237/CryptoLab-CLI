"""Panel widget - replaces render_box (CLI) and render_card (interactive)."""

from typing import Dict, List, Optional
from cryptolab import __version__
from cryptolab.ui.theme import Color, Symbol, Spacing, Width, clip_text, term_width
from cryptolab.ui.widgets.rule import Rule


class Panel:
    """Result panel widget for displaying operation results."""

    @staticmethod
    def result(
        title: str,
        method: str,
        operation: str,
        status: str,
        input_text: str,
        output_text: str,
        reasons: Optional[List[str]] = None,
        extra_fields: Optional[Dict[str, str]] = None,
        width: Optional[int] = None,
    ) -> str:
        """Render a compact result panel (replaces render_card)."""
        w = width or term_width()
        content_width = min(w - 4, 100)

        status_lower = status.lower()
        if any(tok in status_lower for tok in ("gagal", "error", "kesalahan")):
            styled_status = Color.red(status)
        elif any(tok in status_lower for tok in ("berhasil", "ok", "valid")):
            styled_status = Color.green(status)
        else:
            styled_status = Color.yellow(status)

        lines = [
            "",
            f"  {Color.emphasis(title.upper())}",
            f"  {method}  |  {operation}",
            f"  Status: {styled_status}",
        ]

        if extra_fields:
            for k, v in extra_fields.items():
                lines.append(f"  {Color.cyan(k)}: {Color.white(v)}")

        lines.extend([
            "",
            f"  {Color.cyan('Input')}",
            f"  {clip_text(input_text, content_width)}",
            "",
            f"  {Color.cyan('Output')}",
            f"  {clip_text(output_text, content_width)}",
        ])

        if reasons:
            lines.append("")
            lines.append(f"  {Color.yellow('Catatan')}: {'; '.join(reasons)}")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def cli_box(
        title: str,
        operation: str,
        input_text: str,
        output_text: str,
        params: Optional[Dict[str, str]] = None,
        width: int = Width.DIVIDER_CLI,
    ) -> str:
        """Render CLI-style box (replaces render_box) - EXACT match to old render_box."""
        lines = [
            Rule.heavy(width),
            f"  CRYPTOLAB CLI v{__version__} - {title.upper()}",
            Rule.heavy(width),
            f"  Operasi     : {operation}",
        ]
        if params:
            for k, v in params.items():
                lines.append(f"  {k:<12}: {v}")

        lines.extend([
            f"  Status      : BERHASIL (OK)",
            Rule.light(width),
            "  INPUT:",
            f"  {input_text}",
            Rule.light(width),
            "  OUTPUT:",
            f"  {output_text}",
            Rule.heavy(width),
        ])
        return "\n".join(lines)

    @staticmethod
    def error(message: str, width: int = Width.DIVIDER_CLI) -> str:
        """Render error box (replaces render_error) - EXACT match to old render_error."""
        lines = [
            Rule.heavy(width),
            f"  CRYPTOLAB CLI - ERROR: {message}",
            Rule.heavy(width),
        ]
        return "\n".join(lines)

    @staticmethod
    def info_box(title: str, content: str, width: int = Width.DIVIDER_CLI) -> str:
        """Render info box with title and content."""
        lines = [
            Rule.heavy(width),
            f"  {title.upper()}",
            Rule.heavy(width),
            f"  {content}",
            Rule.heavy(width),
        ]
        return "\n".join(lines)

    @staticmethod
    def help_box(category: str, items: List[str], width: int = Width.DIVIDER_CLI) -> str:
        """Render help box with category and items."""
        lines = [
            Rule.heavy(width),
            f"  {category.upper()}",
            Rule.heavy(width),
        ]
        for item in items:
            lines.append(f"  {Symbol.BULLET} {item}")
        lines.append(Rule.heavy(width))
        return "\n".join(lines)

    @staticmethod
    def display(panel_str: str) -> None:
        """Print panel to stdout."""
        print(panel_str)
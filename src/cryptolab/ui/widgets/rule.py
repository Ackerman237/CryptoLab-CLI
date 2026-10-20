"""Rule/Divider widget - replaces all hardcoded divider strings."""

from typing import Optional
from cryptolab.ui.theme import Color, Symbol, Width, term_width


class Rule:
    """Horizontal rule / divider widget."""

    @staticmethod
    def heavy(width: Optional[int] = None, char: str = "=") -> str:
        """Heavy divider (===). Default: CLI width 70."""
        w = width or Width.DIVIDER_CLI
        return Color.dim(char * w)

    @staticmethod
    def light(width: Optional[int] = None, char: str = "-") -> str:
        """Light divider (---). Default: CLI width 70."""
        w = width or Width.DIVIDER_CLI
        return Color.dim(char * w)

    @staticmethod
    def thin(width: Optional[int] = None, char: str = ".") -> str:
        """Thin divider (...). Default: Interactive width 56."""
        w = width or Width.DIVIDER_INTERACTIVE
        return Color.dim(char * w)

    @staticmethod
    def footer(width: Optional[int] = None) -> str:
        """Footer rule using unicode box drawing (─)."""
        w = width or term_width()
        return Color.dim("  " + Symbol.BOX_H * max(w - 4, 0))

    @staticmethod
    def section(title: str, width: Optional[int] = None) -> str:
        """Section divider with centered title (=== TITLE ===)."""
        w = width or Width.DIVIDER_CLI
        if len(title) + 4 > w:
            title = title[: max(w - 7, 0)] + Symbol.ELLIPSIS
        padding = (w - len(title) - 2) // 2
        left = "=" * padding
        right = "=" * (w - len(title) - 2 - padding)
        return Color.dim(f"{left} {title} {right}")

    @staticmethod
    def blank() -> str:
        """Empty line."""
        return ""
"""Design tokens for CryptoLab UI - Single Source of Truth for colors, symbols, spacing."""

import os
import sys
from typing import Optional


class Color:
    """ANSI color tokens - USE THESE INSTEAD OF RAW ESCAPE CODES."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    WHITE = "\033[97m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"

    @classmethod
    def _enabled(cls) -> bool:
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False
        if sys.platform == "win32":
            return (
                os.environ.get("WT_SESSION") is not None
                or "ANSICON" in os.environ
                or os.environ.get("TERM") is not None
            )
        return True

    @classmethod
    def apply(cls, text: str, *styles: str) -> str:
        """Apply styles to text if color is enabled."""
        if not cls._enabled() or not text:
            return text
        style_codes = "".join(styles)
        return f"{style_codes}{text}{cls.RESET}"

    @classmethod
    def red(cls, text: str) -> str:
        return cls.apply(text, cls.RED)

    @classmethod
    def green(cls, text: str) -> str:
        return cls.apply(text, cls.GREEN)

    @classmethod
    def yellow(cls, text: str) -> str:
        return cls.apply(text, cls.YELLOW)

    @classmethod
    def cyan(cls, text: str) -> str:
        return cls.apply(text, cls.CYAN)

    @classmethod
    def white(cls, text: str) -> str:
        return cls.apply(text, cls.WHITE)

    @classmethod
    def bold(cls, text: str) -> str:
        return cls.apply(text, cls.BOLD)

    @classmethod
    def dim(cls, text: str) -> str:
        return cls.apply(text, cls.DIM)

    @classmethod
    def emphasis(cls, text: str) -> str:
        return cls.apply(text, cls.BOLD, cls.WHITE)

    @classmethod
    def muted(cls, text: str) -> str:
        return cls.apply(text, cls.DIM)


class Symbol:
    """Unicode symbol tokens - USE THESE INSTEAD OF RAW CHARACTERS."""

    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    POINTER = "▸"
    BULLET = "•"
    ARROW_UP = "↑"
    ARROW_DOWN = "↓"
    ARROW_LEFT = "←"
    ARROW_RIGHT = "→"
    CHECK = "✓"
    CROSS = "✗"
    ELLIPSIS = "…"
    BOX_H = "─"
    BOX_V = "│"
    BOX_TL = "┌"
    BOX_TR = "┐"
    BOX_BL = "└"
    BOX_BR = "┘"
    BOX_T = "┬"
    BOX_B = "┴"
    BOX_L = "├"
    BOX_R = "┤"
    BOX_X = "┼"


class Spacing:
    """Spacing tokens for consistent layout."""

    INDENT = "  "
    INDENT2 = "    "
    INDENT3 = "      "
    GAP = "   "
    GAP2 = "     "
    PAD = " "
    MARGIN = "\n"


class Width:
    """Default width tokens - responsive fallback values."""

    DEFAULT = 80
    NARROW = 60
    WIDE = 120
    DIVIDER_CLI = 70
    DIVIDER_INTERACTIVE = 56


# ============================================================
# Logo definitions (progressive sizes - block style)
# ============================================================

LOGO_LARGE = """\
▄▀▀▀▀ █▀▀▀▄ █   █ █▀▀▀▄ ▀▀█▀▀ ▄▀▀▀▄ █     ▄▀▀▀▄ █▀▀▀▄
█     █▀▀█   ▀▄▀  █▀▀▀    █   █   █ █     █▀▀▀█ █▀▀▀▄
▀▀▀▀ ▀   ▀   ▀   ▀       ▀    ▀▀▀  ▀▀▀▀▀ ▀   ▀ ▀▀▀▀"""

LOGO_MEDIUM = """\
▄▀▀▀▀ █▀▀▀▄ █   █ █▀▀▀▄
█     █▀▀█   ▀▄▀  █▀▀▀
▀▀▀▀ ▀   ▀   ▀   ▀"""

LOGO_TINY = "CRYPTOLAB"


def pick_logo(width: int, max_rows: int = 99) -> str:
    """Pick largest logo that fits width AND height."""
    for logo in (LOGO_LARGE, LOGO_MEDIUM):
        if _block_width(logo) <= width and len(logo.splitlines()) <= max_rows:
            return logo
    return LOGO_TINY


def term_width(default: int = Width.DEFAULT) -> int:
    """Get terminal width with fallback."""
    try:
        import shutil
        return shutil.get_terminal_size((default, 24)).columns
    except Exception:
        return default


def term_height(default: int = 24) -> int:
    """Get terminal height with fallback."""
    try:
        import shutil
        return shutil.get_terminal_size((80, default)).lines
    except Exception:
        return default


class Style:
    """Composite style presets for common UI patterns."""

    @staticmethod
    def header_text(text: str) -> str:
        return Color.emphasis(text.upper())

    @staticmethod
    def label(key: str) -> str:
        return Color.cyan(key)

    @staticmethod
    def value(val: str) -> str:
        return Color.white(val)

    @staticmethod
    def hint_key(key: str) -> str:
        return Color.emphasis(key)

    @staticmethod
    def hint_label(label: str) -> str:
        return Color.dim(label)

    @staticmethod
    def divider_heavy(width: int = Width.DIVIDER_CLI) -> str:
        return Color.dim("=" * width)

    @staticmethod
    def divider_light(width: int = Width.DIVIDER_CLI) -> str:
        return Color.dim("-" * width)

    @staticmethod
    def divider_thin(width: int = Width.DIVIDER_INTERACTIVE) -> str:
        return Color.dim("." * width)

    @staticmethod
    def footer_rule(width: int) -> str:
        return Color.dim("  " + Symbol.BOX_H * max(width - 4, 0))


def _block_width(text: str) -> int:
    """Get max line width of a multi-line string."""
    return max(len(line) for line in text.splitlines())


def center_block(text: str, width: int, offset: int = 0) -> str:
    """Center a multi-line block within width, with optional offset."""
    lines = text.splitlines()
    return "\n".join(line.center(width + offset) for line in lines)


def clip_text(text: str, width: int) -> str:
    """Clip text to width with ellipsis."""
    return text if len(text) <= width else text[: max(width - 1, 0)] + Symbol.ELLIPSIS


def fit_hints(hints: list[tuple[str, str]], width: int, gap: int = 3) -> list[tuple[str, str]]:
    """Fit hints to terminal width by dropping from end."""
    chosen = list(hints)
    while chosen:
        if len((" " * gap).join(f"{k} {l}" for k, l in chosen)) <= width - 2:
            return chosen
        chosen.pop()
    return []


# Standard hint sets
HINTS_MAIN = [
    (Symbol.ARROW_UP + Symbol.ARROW_DOWN, "navigasi"),
    ("enter", "pilih"),
    ("q", "keluar"),
    ("?", "bantuan"),
]

HINTS_SUB = [
    (Symbol.ARROW_UP + Symbol.ARROW_DOWN, "navigasi"),
    ("enter", "pilih"),
    ("esc", "kembali"),
    ("q", "keluar"),
    ("?", "bantuan"),
]
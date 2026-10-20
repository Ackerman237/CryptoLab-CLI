"""Design tokens for CryptoLab UI - Single Source of Truth for colors, symbols, spacing."""

import os
import re
import sys
from typing import Optional

# Regex untuk melucuti kode ANSI saat menghitung panjang terlihat.
_ANSI = re.compile(r"\033\[[0-9;?]*[A-Za-z]")


def vlen(s: str) -> int:
    """Panjang teks yang terlihat (tanpa kode ANSI)."""
    return len(_ANSI.sub("", s))


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

    # Unicode symbols
    _SUCCESS_UNI = "✓"
    _ERROR_UNI = "✗"
    _WARNING_UNI = "⚠"
    _INFO_UNI = "ℹ"
    _POINTER_UNI = "▸"
    _BULLET_UNI = "•"
    _ARROW_UP_UNI = "↑"
    _ARROW_DOWN_UNI = "↓"
    _ARROW_LEFT_UNI = "←"
    _ARROW_RIGHT_UNI = "→"
    _CHECK_UNI = "✓"
    _CROSS_UNI = "✗"
    _ELLIPSIS_UNI = "…"
    _BOX_H_UNI = "─"
    _BOX_V_UNI = "│"
    _BOX_TL_UNI = "┌"
    _BOX_TR_UNI = "┐"
    _BOX_BL_UNI = "└"
    _BOX_BR_UNI = "┘"
    _BOX_T_UNI = "┬"
    _BOX_B_UNI = "┴"
    _BOX_L_UNI = "├"
    _BOX_R_UNI = "┤"
    _BOX_X_UNI = "┼"

    # ASCII fallbacks
    _SUCCESS_ASCII = "+"
    _ERROR_ASCII = "x"
    _WARNING_ASCII = "!"
    _INFO_ASCII = "i"
    _POINTER_ASCII = ">"
    _BULLET_ASCII = "*"
    _ARROW_UP_ASCII = "^"
    _ARROW_DOWN_ASCII = "v"
    _ARROW_LEFT_ASCII = "<"
    _ARROW_RIGHT_ASCII = ">"
    _CHECK_ASCII = "+"
    _CROSS_ASCII = "x"
    _ELLIPSIS_ASCII = "..."
    _BOX_H_ASCII = "-"
    _BOX_V_ASCII = "|"
    _BOX_TL_ASCII = "+"
    _BOX_TR_ASCII = "+"
    _BOX_BL_ASCII = "+"
    _BOX_BR_ASCII = "+"
    _BOX_T_ASCII = "+"
    _BOX_B_ASCII = "+"
    _BOX_L_ASCII = "+"
    _BOX_R_ASCII = "+"
    _BOX_X_ASCII = "+"

    @classmethod
    def _unicode_supported(cls) -> bool:
        """Check if the terminal supports Unicode output."""
        import sys
        import os
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False
        if sys.platform == "win32":
            return (
                os.environ.get("WT_SESSION") is not None
                or "ANSICON" in os.environ
                or os.environ.get("TERM") is not None
            )
        return True

    # Determine Unicode support at class definition time
    _unicode_ok = _unicode_supported.__func__(None)

    # Public attributes - set based on Unicode support
    if _unicode_ok:
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
    else:
        SUCCESS = "+"
        ERROR = "x"
        WARNING = "!"
        INFO = "i"
        POINTER = ">"
        BULLET = "*"
        ARROW_UP = "^"
        ARROW_DOWN = "v"
        ARROW_LEFT = "<"
        ARROW_RIGHT = ">"
        CHECK = "+"
        CROSS = "x"
        ELLIPSIS = "..."
        BOX_H = "-"
        BOX_V = "|"
        BOX_TL = "+"
        BOX_TR = "+"
        BOX_BL = "+"
        BOX_BR = "+"
        BOX_T = "+"
        BOX_B = "+"
        BOX_L = "+"
        BOX_R = "+"
        BOX_X = "+"


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

# Large block-style CRYPTOLAB logo (5 lines) - matches banner.py
_LOGO_LARGE_UNI = """\
██████  ██████  ██    ██ ██████  ████████  ██████  ██       █████  ██████
██      ██   ██  ██  ██  ██   ██ ██    ██ ██   ██ ██      ██   ██ ██   ██
██      ██████    ████   ██████  ██    ██ ██████  ██      ███████ ██████
██      ██   ██    ██    ██      ██    ██ ██   ██ ██      ██   ██ ██   ██
 ██████ ██   ██    ██    ██      ██     ██████  ███████ ██   ██ ██   ██"""

# Medium block-style logo (3 lines) - condensed version
_LOGO_MEDIUM_UNI = """\
██████ ██████ ██  ██ ██████ ████████ ██████ ██    █████ ██████
██     ██  ██ ██ ██  ██  ██ ██    ██ ██     ██   ██ ██   ██
██     ██████ ████   ██████ ██    ██ █████  ██   ███████ ██████
██     ██  ██ ██ ██  ██     ██    ██ ██     ██   ██ ██   ██
 ██████ ██  ██ ██  ██ ██     ██     ██████ ███████ ██ ██   ██"""

# Small logo for very narrow terminals
_LOGO_SMALL_UNI = """\
██████ ██████ ██████ ██    ██ ███████ ██████
██     ██  ██ ██   ██ ██  ██ ██      ██   ██
█████  ██████ ██████ ██████ █████   ██████
██     ██  ██ ██   ██ ██ ██ ██      ██   ██
██████ ██  ██ ██      ████  ███████ ██   ██"""

# ASCII fallback matching the geometric shape of the SVG logo.
_LOGO_LARGE_ASCII = """\
  ####  ####  ####  ####  ####  ####  ####  ####  ####
 #      #      #  #  #      #      #  #  #  #  #      #
 #      ####   ####  ####   #      ####  #  #  ####   #
 #      #      # #   #      #      #  #  #  #  #      #
  ####  ####  #  #  ####    ####  #  #  #  #  ####   #"""

_LOGO_MEDIUM_ASCII = """\
 #### #### #  # #### ###### ####  #   #### ####
 #    #  # # # #  #   #   #  # # # #     #  #
 ####  #### ####   ####   ####  #  #  ###  ####
 #    #  # # # #  #   #   #  # # # #     #  #
 #### #  # #  # ####    ####  #   #### #  #"""

LOGO_TINY = "CRYPTOLAB"


def _unicode_supported() -> bool:
    """Check if the terminal supports Unicode output."""
    import sys
    import os
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        return (
            os.environ.get("WT_SESSION") is not None
            or "ANSICON" in os.environ
            or os.environ.get("TERM") is not None
        )
    return True


# Set logos based on Unicode support
if _unicode_supported():
    LOGO_LARGE = _LOGO_LARGE_UNI
    LOGO_MEDIUM = _LOGO_MEDIUM_UNI
else:
    LOGO_LARGE = _LOGO_LARGE_ASCII
    LOGO_MEDIUM = _LOGO_MEDIUM_ASCII


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
    """Get max *visible* line width of a multi-line string (ANSI stripped)."""
    return max((vlen(line) for line in text.splitlines()), default=0)


def center_block(text: str, width: int, offset: int = 0) -> str:
    """Center a multi-line block as ONE BLOCK (padding same for all lines).

    Semua baris diberi padding yang sama berdasarkan lebar blok terlihat,
    sehingga tepi kiri semua baris sejajar.
    """
    lines = text.splitlines()
    bw = max((vlen(l) for l in lines), default=0)
    pad = " " * max((width - bw) // 2, 0)
    return "\n".join(pad + l.ljust(bw) for l in lines)


def clip_text(text: str, width: int) -> str:
    """Clip text to visible width with ellipsis."""
    return text if vlen(text) <= width else text[: max(width - 1, 0)] + Symbol.ELLIPSIS


def fit_hints(hints: list[tuple[str, str]], width: int, gap: int = 3) -> list[tuple[str, str]]:
    """Fit hints to terminal width by dropping from end. Uses vlen for accuracy."""
    chosen = list(hints)
    while chosen:
        plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
        if vlen(plain) <= width - 2:
            return chosen
        chosen.pop()
    return []


def render_footer(hints: list[tuple[str, str]], width: int) -> str:
    """Render footer with thin rule and centered hints (vlen for alignment)."""
    chosen = list(hints)
    while chosen:
        plain = (" " * 3).join(f"{k} {l}" for k, l in chosen)
        if vlen(plain) <= width - 2:
            break
        chosen.pop()
    styled = (" " * 3).join(f"{Color.emphasis(k)} {Color.dim(l)}" for k, l in chosen)
    rule = Color.dim("  " + Symbol.BOX_H * max(width - 4, 0))
    return rule + "\n" + " " * max((width - vlen(plain)) // 2, 0) + styled


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


def render_header(subtitle: str = "", max_logo_rows: int = 99) -> str:
    """Render header with logo, blank line, and subtitle (uses vlen for ANSI-safe checks)."""
    w = term_width()
    logo = Color.emphasis(center_block(pick_logo(w, max_logo_rows), w))
    if subtitle:
        if vlen(subtitle) > w:
            subtitle = subtitle.split(" · ")[0]
        if vlen(subtitle) > w:
            subtitle = subtitle[: max(w - 1, 0)] + Symbol.ELLIPSIS
        sub = Color.dim(subtitle.center(w))
        return "\n".join(["", logo, "", sub])
    return "\n".join(["", logo])
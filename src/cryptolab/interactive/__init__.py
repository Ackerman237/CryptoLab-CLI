"""Interactive Package - Terminal Interface for CryptoLab."""

from cryptolab.ui import Color, Symbol, term_width, term_height, center_block, render_footer, render_header, HINTS_MAIN, HINTS_SUB
from cryptolab.ui.widgets.menu import Menu, navigation_menu
from cryptolab.interactive.menu import get_main_menu_labels, get_main_menu_handlers, get_header_subtitle
from cryptolab.interactive.handlers import (
    handle_auto_analyze,
    handle_caesar,
    handle_vigenere,
    handle_playfair,
    handle_hill,
    handle_affine,
    handle_railfence,
    handle_des,
    handle_aes,
    handle_rc2,
    handle_hashing,
    handle_rsa,
    handle_dh,
    handle_base64,
    handle_hex,
    handle_binary,
    handle_history,
)

# Backward compatibility - internal functions used by tests
from cryptolab.ui.layout import clear_screen, hide_cursor, show_cursor

_render_header = render_header

def _clip(text: str, width: int) -> str:
    """Clip text to width with ellipsis."""
    from cryptolab.ui import Symbol
    return text if len(text) <= width else text[: max(width - 1, 0)] + Symbol.ELLIPSIS


def render_menu(labels, selected, descs=None, avail_rows=None):
    """Menu satu kolom: blok dipusatkan, tepi kiri SEJAJAR, ada scroll jika layar pendek."""
    w = term_width()
    n = len(labels)
    label_w = min(max(len(l) for l in labels), max(w - 6, 8))
    pad = " " * max((w - (2 + label_w)) // 2, 0)

    # viewport
    rows = n if avail_rows is None else avail_rows
    if n <= rows:
        start, end, truncated = 0, n, False
    else:
        view = max(rows - 2, 1)  # sisakan 2 baris untuk penanda ↑/↓
        start = min(max(selected - view // 2, 0), n - view)
        end, truncated = start + view, True

    lines = []
    if truncated:
        lines.append(pad + Color.dim(f"  {Symbol.ARROW_UP} {start} lagi") if start else "")
    for i in range(start, end):
        text = _clip(labels[i], label_w)
        if i == selected:
            lines.append(pad + Color.emphasis(f"{Symbol.POINTER} {text}"))
        else:
            lines.append(pad + Color.dim(f"  {text}"))
    if truncated:
        left = n - end
        lines.append(pad + Color.dim(f"  {Symbol.ARROW_DOWN} {left} lagi") if left else "")

    # deskripsi item terpilih (selalu 2 baris: kosong + teks)
    desc = (descs[selected] if descs else "") or ""
    desc = _clip(desc, w - 4)
    lines.append("")
    lines.append(" " * max((w - len(desc)) // 2, 0) + Color.dim(desc) if desc else "")
    return lines


def menu_lines(menu, sel, depth):
    h = term_height()
    labels = [it[0] for it in menu.items]
    descs = [it[2] if len(it) > 2 else "" for it in menu.items]
    hints = HINTS_SUB if depth > 0 else HINTS_MAIN

    # Total baris = header(logo+3) + 3 (kosong, judul, kosong) + menu + 2 (kosong, deskripsi)
    #               + 1 (kosong) + 2 (garis + hint) = header + menu + 8
    want_menu = min(len(labels), 10)
    logo_rows = max(h - 11 - want_menu, 1)
    header = _render_header(get_header_subtitle(), max_logo_rows=logo_rows).split("\n")

    avail = max(h - len(header) - 8, 3)
    body = render_menu(labels, sel, descs, avail_rows=avail)
    w = term_width()
    lines = header + ["", Color.dim(center_block(menu.title, w)), ""] + body + ["", render_footer(hints, w)]
    return lines[:h]


def draw_menu(menu, sel, depth, full_clear):
    screen(menu_lines(menu, sel, depth), full_clear)


def screen(lines, full_clear: bool):
    """Render lines to terminal with optional full clear."""
    import sys
    output = []
    if full_clear:
        output.append("\033[2J\033[H")
    else:
        output.append("\033[H")
    output.extend(line + "\n" for line in lines)
    sys.stdout.write("".join(output))
    sys.stdout.flush()


# Export old Menu class for backward compatibility
class Menu:
    """Simple menu container with title and items (backward compatibility)."""

    def __init__(self, title: str, items: list):
        self.title = title
        self.items = items


HEADER_SUBTITLE = "CRYPTOLAB CLI v0.1.0 · TOOLKIT KRIPTOGRAFI & ENCODING"

__all__ = [
    "get_main_menu_labels",
    "get_main_menu_handlers",
    "get_header_subtitle",
    "navigation_menu",
    "Menu",
    "render_menu",
    "menu_lines",
    "draw_menu",
    "screen",
    "_clip",
    "render_header",
    "term_width",
    "term_height",
    "HEADER_SUBTITLE",
    "HINTS_MAIN",
    "HINTS_SUB",
    # Classical
    "handle_caesar",
    "handle_vigenere",
    "handle_playfair",
    "handle_hill",
    "handle_affine",
    "handle_railfence",
    # Symmetric
    "handle_des",
    "handle_aes",
    "handle_rc2",
    # Hashing
    "handle_hashing",
    # Asymmetric
    "handle_rsa",
    "handle_dh",
    # Encoding
    "handle_base64",
    "handle_hex",
    "handle_binary",
    # Analysis
    "handle_auto_analyze",
    # History
    "handle_history",
]
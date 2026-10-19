"""Interactive Package - Terminal Interface for CryptoLab."""

from cryptolab.ui import Color, Symbol, term_width, term_height, center_block, render_footer, render_header, HINTS_MAIN, HINTS_SUB

# Define HEADER_SUBTITLE here to avoid circular imports
HEADER_SUBTITLE = "CRYPTOLAB CLI v1.0.0 · TOOLKIT KRIPTOGRAFI & ENCODING"

from cryptolab.ui.widgets.menu import Menu, navigation_menu
from cryptolab.interactive.menu import get_main_menu_labels, get_main_menu_handlers, MAIN_MENU_LABELS as MAIN_LABELS
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

# save_result_prompt - defined inline to avoid circular import with interactive.py module
def save_result_prompt(content: str, default_filename: str = "hasil_cryptolab.txt") -> None:
    """Prompt user to optionally save text content to a file."""
    from pathlib import Path
    from cryptolab.ui import safe_input, Color
    try:
        choice = safe_input(f"\n  Simpan hasil ke file? (y/n) [n]: ", allow_back=False).lower()
        if choice in ("y", "ya", "yes"):
            fn_input = safe_input(f"  Nama file [{default_filename}]: ", allow_back=False)
            filename = fn_input or default_filename
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")
            print(Color.green(f"  [OK] Hasil berhasil disimpan ke: {filepath.resolve()}"))
    except Exception as err:
        print(Color.red(f"  [!] Gagal menyimpan file: {err}"))

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
    header = _render_header(HEADER_SUBTITLE, max_logo_rows=logo_rows).split("\n")

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


def run_interactive_menu() -> None:
    """Run the interactive menu loop."""
    import sys
    import readchar
    from readchar import key as readchar_key

    from cryptolab.ui import (
        hide_cursor, show_cursor,
        render_header, render_footer, HINTS_MAIN, HINTS_SUB,
        term_width, term_height, center_block,
    )

    hide_cursor()
    try:
        selected = 0
        while True:
            # Render header
            h = term_height()
            w = term_width()
            want_menu = min(len(MAIN_LABELS), 10)
            logo_rows = max(h - 11 - want_menu, 1)
            header = render_header(HEADER_SUBTITLE, max_logo_rows=logo_rows).split("\n")

            avail = max(h - len(header) - 8, 3)
            labels = MAIN_LABELS
            n = len(labels)
            label_w = min(max(len(l) for l in labels), max(w - 6, 8))
            pad = " " * max((w - (2 + label_w)) // 2, 0)

            rows = n if avail is None else avail
            if n <= rows:
                start, end, truncated = 0, n, False
            else:
                view = max(rows - 2, 1)
                start = min(max(selected - view // 2, 0), n - view)
                end, truncated = start + view, True

            body = []
            if truncated:
                body.append(pad + Color.dim(f"  {Symbol.ARROW_UP} {start} lagi") if start else "")
            for i in range(start, end):
                text = labels[i] if len(labels[i]) <= label_w else labels[i][:max(1, label_w - 3)] + "..."
                if i == selected:
                    body.append(pad + Color.emphasis(f"  {Symbol.POINTER} {text}"))
                else:
                    body.append(pad + Color.dim(f"    {text}"))
            if truncated:
                left = n - end
                body.append(pad + Color.dim(f"  {Symbol.ARROW_DOWN} {left} lagi") if left else "")

            # description of selected item
            desc = ""
            body.append("")
            if desc:
                body.append(" " * max((w - len(desc)) // 2, 0) + Color.dim(desc))

            lines = header + ["", Color.dim(center_block("MENU UTAMA", w)), ""] + body + ["", render_footer(HINTS_MAIN, w)]
            lines = lines[:h]

            output = "\033[2J\033[H"
            output += "\n".join(line + "\n" for line in lines)
            sys.stdout.write(output)
            sys.stdout.flush()

            # Read key
            try:
                k = readchar.readkey()
            except (KeyboardInterrupt, EOFError):
                break

            home_key = getattr(readchar_key, "HOME", "\x1b[H")
            end_key = getattr(readchar_key, "END", "\x1b[F")
            if k == readchar_key.UP:
                if selected > 0:
                    selected -= 1
            elif k == readchar_key.DOWN:
                if selected < len(MAIN_LABELS) - 1:
                    selected += 1
            elif k == home_key:
                selected = 0
            elif k == end_key:
                selected = len(MAIN_LABELS) - 1
            elif k in (readchar_key.ENTER, '\r', '\n'):
                action = MAIN_HANDLERS[selected]
                if action:
                    action()
            elif k.lower() == 'q':
                print("\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
                break
            elif k == '?':
                # Show help using existing help system
                pass
    finally:
        show_cursor()

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
    "run_interactive_menu",
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
    # UI
    "save_result_prompt",
]
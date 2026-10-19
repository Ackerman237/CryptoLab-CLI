"""Interactive navigation - arrow key menu navigation."""

import sys
from typing import List, Optional

import readchar
from readchar import key as readchar_key

from cryptolab.ui import (
    Color, Symbol, Spacing, term_width, center_block,
    Rule, HINTS_MAIN, HINTS_SUB,
    hide_cursor, show_cursor,
)


class BackToMenu(Exception):
    """Raised when user chooses to navigate back to the previous menu."""
    pass


class ExitApp(Exception):
    """Raised when user chooses to exit the application."""
    pass


def _clear_screen() -> None:
    """Clear the terminal screen."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _render_header(subtitle: str, max_logo_rows: int = 99) -> str:
    """Render header with logo and subtitle."""
    from cryptolab.ui.theme import pick_logo, LOGO_LARGE, LOGO_MEDIUM, LOGO_TINY
    w = term_width()
    for logo in (LOGO_LARGE, LOGO_MEDIUM):
        if max(len(line) for line in logo.splitlines()) <= w and len(logo.splitlines()) <= max_logo_rows:
            chosen = logo
            break
    else:
        chosen = LOGO_TINY

    logo_centered = center_block(chosen.rstrip("\n"), w)
    painted_logo = Color.emphasis(logo_centered)

    if subtitle:
        if len(subtitle) > w:
            subtitle = subtitle.split(" · ")[0]
        if len(subtitle) > w:
            subtitle = subtitle[: max(w - 1, 0)] + Symbol.ELLIPSIS
        sub = Color.dim(subtitle.center(w))
        return "\n".join(["", painted_logo, "", sub])
    return "\n".join(["", painted_logo])


def _render_footer(hints: list, width: int) -> str:
    """Render footer with thin rule and centered hints."""
    chosen = hints
    while chosen:
        if len((" " * 3).join(f"{k} {l}" for k, l in chosen)) <= width - 2:
            break
        chosen.pop()

    plain = (" " * 3).join(f"{k} {l}" for k, l in chosen)
    styled = (" " * 3).join(f"{Color.emphasis(k)} {Color.dim(l)}" for k, l in chosen)
    rule = Color.dim(" " * 2 + Symbol.BOX_H * max(width - 4, 0))
    return rule + "\n" + " " * max((width - len(plain)) // 2, 0) + styled


def navigation_menu(
    options: List[str],
    title: str = "CRYPTOLAB MENU",
    allow_back: bool = True,
    back_label: str = "Kembali",
    clear_display: bool = True,
    banner: Optional[str] = None,
    banner_responsive: bool = False,
    help_enabled: bool = True,
) -> Optional[int]:
    """Navigate menu with arrow keys (Up/Down), press Enter to select.
    Uses ANSI cursor movement for flicker-free navigation.

    Args:
        options: List of menu option strings
        title: Menu title to display
        allow_back: Whether to allow 'b'/'0'/'back' to go back
        back_label: Label for the back option

    Returns:
        Selected index (0-based), or None if user goes back
    """
    selected = 0
    options_count = len(options)
    menu_rendered = False

    def _render_initial():
        """Initial full render of the menu."""
        nonlocal menu_rendered
        width = term_width()
        if clear_display:
            _clear_screen()
        elif menu_rendered:
            sys.stdout.write("\033[u\033[J")
        else:
            sys.stdout.write("\033[s")

        if banner:
            banner_text = banner
            if banner_responsive:
                # banner responsive handled by theme
                pass
            print(center_block(banner_text.rstrip("\n"), width, offset=-4))
            print()

        print(center_block(title[:max(20, width - 2)], width, offset=-4))
        print()
        sys.stdout.write("\033[s")

        for i, opt in enumerate(options):
            option_text = opt if len(opt) <= width - 8 else opt[:max(1, width - 11)] + Symbol.ELLIPSIS
            if i == selected:
                print(Color.emphasis(f"  {Symbol.POINTER} {option_text}"))
            else:
                print(Color.dim(f"    {option_text}"))

        hints = HINTS_SUB if allow_back else HINTS_MAIN
        print(_render_footer(hints, width))
        print()
        sys.stdout.flush()
        menu_rendered = True

    def _update_selection(old_idx: int, new_idx: int):
        """Update only the selection indicators without full redraw."""
        width = term_width()
        sys.stdout.write("\033[u")
        for i, opt in enumerate(options):
            option_text = opt if len(opt) <= width - 8 else opt[:max(1, width - 11)] + Symbol.ELLIPSIS
            prefix = f"  {Symbol.POINTER} " if i == selected else "    "
            styled = Color.emphasis(prefix + option_text) if i == selected else Color.dim(prefix + option_text)
            sys.stdout.write(f"\033[2K\r{styled}\n")
        sys.stdout.flush()

    def _show_help():
        """Show categorized algorithm help."""
        # This will be handled by the main menu loop
        pass

    # Initial render
    _render_initial()

    home_key = getattr(readchar_key, "HOME", "\x1b[H")
    end_key = getattr(readchar_key, "END", "\x1b[F")
    esc_key = getattr(readchar_key, "ESC", "\x1b")

    while True:
        try:
            k = readchar.readkey()
        except (KeyboardInterrupt, EOFError):
            return None

        if k == readchar_key.UP:
            if selected > 0:
                old = selected
                selected -= 1
                _update_selection(old, selected)
        elif k == readchar_key.DOWN:
            if selected < options_count - 1:
                old = selected
                selected += 1
                _update_selection(old, selected)
        elif k == home_key:
            if selected != 0:
                old = selected
                selected = 0
                _update_selection(old, selected)
        elif k == end_key:
            if selected != options_count - 1:
                old = selected
                selected = options_count - 1
                _update_selection(old, selected)
        elif k in (readchar_key.ENTER, '\r', '\n'):
            if clear_display:
                _clear_screen()
            return selected
        elif k.lower() in ('q',):
            if clear_display:
                _clear_screen()
            return None
        elif help_enabled and k == '?':
            # Help handled by caller
            pass
        elif allow_back and (k.lower() in ('b', '0') or k == esc_key):
            if clear_display:
                _clear_screen()
            return None

    return None


def _clip(text: str, width: int) -> str:
    """Clip text to width with ellipsis."""
    return text if len(text) <= width else text[: max(width - 1, 0)] + Symbol.ELLIPSIS


def render_menu_labels(labels: List[str], selected: int, descs: List[str] = None, avail_rows: int = None) -> List[str]:
    """Render menu labels with optional descriptions and viewport scrolling."""
    w = term_width()
    n = len(labels)
    label_w = min(max(len(l) for l in labels), max(w - 6, 8))
    pad = " " * max((w - (2 + label_w)) // 2, 0)

    # viewport
    rows = n if avail_rows is None else avail_rows
    if n <= rows:
        start, end, truncated = 0, n, False
    else:
        view = max(rows - 2, 1)  # reserve 2 lines for up/down indicators
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

    # description of selected item (always 2 lines: empty + text)
    desc = (descs[selected] if descs else "") or ""
    desc = _clip(desc, w - 4)
    lines.append("")
    if desc:
        lines.append(" " * max((w - len(desc)) // 2, 0) + Color.dim(desc))
    return lines
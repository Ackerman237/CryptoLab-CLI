"""Layout utilities - screen clearing, cursor control, alt screen."""

import sys
from cryptolab.ui.theme import term_width, term_height


def clear_screen() -> None:
    """Clear entire screen and move cursor to home."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def clear_from_cursor() -> None:
    """Clear from cursor to end of screen."""
    sys.stdout.write("\033[J")
    sys.stdout.flush()


def clear_line() -> None:
    """Clear current line."""
    sys.stdout.write("\033[2K\r")
    sys.stdout.flush()


def save_cursor() -> None:
    """Save cursor position."""
    sys.stdout.write("\033[s")
    sys.stdout.flush()


def restore_cursor() -> None:
    """Restore cursor position."""
    sys.stdout.write("\033[u")
    sys.stdout.flush()


def hide_cursor() -> None:
    """Hide cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """Show cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def alt_screen_enter() -> None:
    """Enter alternate screen buffer."""
    sys.stdout.write("\033[?1049h\033[2J\033[H")
    sys.stdout.flush()


def alt_screen_exit() -> None:
    """Exit alternate screen buffer."""
    sys.stdout.write("\033[?1049l")
    sys.stdout.flush()


def move_cursor_up(n: int = 1) -> None:
    """Move cursor up N lines."""
    if n > 0:
        sys.stdout.write(f"\033[{n}A")
        sys.stdout.flush()


def move_cursor_down(n: int = 1) -> None:
    """Move cursor down N lines."""
    if n > 0:
        sys.stdout.write(f"\033[{n}B")
        sys.stdout.flush()


def move_cursor_to(row: int, col: int = 1) -> None:
    """Move cursor to specific position (1-indexed)."""
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


class ScreenContext:
    """Context manager for alternate screen."""

    def __enter__(self) -> "ScreenContext":
        alt_screen_enter()
        hide_cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        show_cursor()
        alt_screen_exit()


def get_terminal_size() -> tuple[int, int]:
    """Get (width, height) of terminal."""
    return term_width(), term_height()
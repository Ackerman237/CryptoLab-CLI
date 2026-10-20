"""Menu & Navigation widget - arrow key navigation, selection."""

import sys
from typing import List, Optional, Callable

import readchar
from readchar import key as readchar_key

from cryptolab.ui.theme import Color, Symbol, Spacing, term_width, center_block, pick_logo, HINTS_MAIN, HINTS_SUB
from cryptolab.ui.widgets.rule import Rule


class BackToMenu(Exception):
    """Raised when user chooses to navigate back."""
    pass


class ExitApp(Exception):
    """Raised when user chooses to exit the application."""
    pass


class Menu:
    """Interactive menu with arrow key navigation."""

    def __init__(
        self,
        options: List[str],
        title: str = "CRYPTOLAB MENU",
        allow_back: bool = True,
        back_label: str = "Kembali",
        clear_display: bool = True,
        banner: Optional[str] = None,
        banner_responsive: bool = False,
        help_enabled: bool = True,
        help_callback: Optional[Callable] = None,
    ):
        self.options = options
        self.title = title
        self.allow_back = allow_back
        self.back_label = back_label
        self.clear_display = clear_display
        self.banner = banner
        self.banner_responsive = banner_responsive
        self.help_enabled = help_enabled
        self.help_callback = help_callback

        self.selected = 0
        self.options_count = len(options)
        self.menu_rendered = False
        self.width = term_width()

    def _clear_screen(self) -> None:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def _render_initial(self) -> None:
        """Initial full render of the menu."""
        self.width = term_width()
        if self.clear_display:
            self._clear_screen()
        elif self.menu_rendered:
            sys.stdout.write("\033[u\033[J")
        else:
            sys.stdout.write("\033[s")

        if self.banner:
            banner_text = pick_logo(self.width) if self.banner_responsive else self.banner
            print(center_block(banner_text.rstrip("\n"), self.width, offset=-4))
            print()

        print(center_block(self.title[:max(20, self.width - 2)], self.width, offset=-4))
        print()
        sys.stdout.write("\033[s")

        for i, opt in enumerate(self.options):
            option_text = opt if len(opt) <= self.width - 8 else opt[:max(1, self.width - 11)] + Symbol.ELLIPSIS
            if i == self.selected:
                print(Color.emphasis(f"  {Symbol.POINTER} {option_text}"))
            else:
                print(Color.muted(f"    {option_text}"))

        hints = HINTS_SUB if self.allow_back else HINTS_MAIN
        print(Rule.footer(self.width))
        print()
        sys.stdout.flush()
        self.menu_rendered = True

    def _update_selection(self, old_idx: int, new_idx: int) -> None:
        """Update only the selection indicators without full redraw."""
        self.width = term_width()
        sys.stdout.write("\033[u")
        for i, opt in enumerate(self.options):
            option_text = opt if len(opt) <= self.width - 8 else opt[:max(1, self.width - 11)] + Symbol.ELLIPSIS
            prefix = f"  {Symbol.POINTER} " if i == self.selected else "    "
            styled = Color.emphasis(prefix + option_text) if i == self.selected else Color.muted(prefix + option_text)
            sys.stdout.write(f"\033[2K\r{styled}\n")
        sys.stdout.flush()

    def _show_help(self) -> None:
        """Show help - either callback or default category help."""
        if self.help_callback:
            self.help_callback()
            self._render_initial()
            return

    def run(self) -> Optional[int]:
        """Run the menu loop. Returns selected index (0-based) or None if back/exit."""
        self._render_initial()

        home_key = getattr(readchar_key, "HOME", "\x1b[H")
        end_key = getattr(readchar_key, "END", "\x1b[F")
        esc_key = getattr(readchar_key, "ESC", "\x1b")

        while True:
            try:
                k = readchar.readkey()
            except (KeyboardInterrupt, EOFError):
                return None

            if k == readchar_key.UP:
                if self.selected > 0:
                    old = self.selected
                    self.selected -= 1
                    self._update_selection(old, self.selected)
            elif k == readchar_key.DOWN:
                if self.selected < self.options_count - 1:
                    old = self.selected
                    self.selected += 1
                    self._update_selection(old, self.selected)
            elif k == home_key:
                if self.selected != 0:
                    old = self.selected
                    self.selected = 0
                    self._update_selection(old, self.selected)
            elif k == end_key:
                if self.selected != self.options_count - 1:
                    old = self.selected
                    self.selected = self.options_count - 1
                    self._update_selection(old, self.selected)
            elif k in (readchar_key.ENTER, '\r', '\n'):
                if self.clear_display:
                    self._clear_screen()
                return self.selected
            elif k.lower() in ('q',):
                if self.clear_display:
                    self._clear_screen()
                return None
            elif self.help_enabled and k == '?':
                self._show_help()
            elif self.allow_back and (k.lower() in ('b', '0') or k == esc_key):
                if self.clear_display:
                    self._clear_screen()
                return None

        return None


def navigation_menu(
    options: List[str],
    title: str = "CRYPTOLAB MENU",
    allow_back: bool = True,
    back_label: str = "Kembali",
    clear_display: bool = True,
    banner: Optional[str] = None,
    banner_responsive: bool = False,
    help_enabled: bool = True,
    help_callback: Optional[Callable] = None,
) -> Optional[int]:
    """Convenience function for simple menu navigation."""
    menu = Menu(
        options=options,
        title=title,
        allow_back=allow_back,
        back_label=back_label,
        clear_display=clear_display,
        banner=banner,
        banner_responsive=banner_responsive,
        help_enabled=help_enabled,
        help_callback=help_callback,
    )
    return menu.run()
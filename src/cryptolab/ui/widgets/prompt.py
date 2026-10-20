"""Prompt widget - unified user input handling (ask, choose, confirm)."""

import sys
from typing import Optional, List, Any

from cryptolab.ui.theme import Color, Symbol, Spacing


class Prompt:
    """Unified prompt handling for user input."""

    @staticmethod
    def _read_line(prompt: str) -> str:
        """Read a line from stdin with prompt."""
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            print()
            raise

    @staticmethod
    def ask(label: str, default: str = "", allow_empty: bool = False, allow_back: bool = True) -> Optional[str]:
        """Ask for text input with optional default and back navigation."""
        back_hint = " (b/kembali untuk batal)" if allow_back else ""
        default_hint = f" [{default}]" if default else ""
        full_prompt = f"{Spacing.INDENT}{Color.cyan(label)}{default_hint}{back_hint}: "

        while True:
            try:
                val = Prompt._read_line(full_prompt).strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if allow_back and val.lower() in ("b", "kembali", "back"):
                return None

            if val:
                return val
            if default:
                return default
            if allow_empty:
                return ""
            Message.print_warning("Input tidak boleh kosong")

    @staticmethod
    def ask_int(label: str, default: int = 0, min_val: int = None, max_val: int = None, allow_back: bool = True) -> Optional[int]:
        """Ask for integer input with validation."""
        while True:
            val = Prompt.ask(label, default=str(default) if default else "", allow_back=allow_back)
            if val is None:
                return None
            try:
                num = int(val)
                if min_val is not None and num < min_val:
                    Message.print_warning(f"Nilai minimal: {min_val}")
                    continue
                if max_val is not None and num > max_val:
                    Message.print_warning(f"Nilai maksimal: {max_val}")
                    continue
                return num
            except ValueError:
                Message.print_warning("Masukkan angka bulat yang valid")

    @staticmethod
    def choose(label: str, options: List[str], default: int = 0, allow_back: bool = True) -> Optional[int]:
        """Choose from a list of options by number (1-based display, 0-based return)."""
        if not options:
            Message.print_error("Tidak ada opsi tersedia")
            return None

        print(f"\n{Spacing.INDENT}{Color.emphasis(label)}")
        for i, opt in enumerate(options, 1):
            print(f"{Spacing.INDENT2}{Color.dim(f'{i}.')} {opt}")

        if allow_back:
            print(f"{Spacing.INDENT2}{Color.dim('0.')} Kembali")

        max_choice = len(options)
        min_choice = 1
        default_display = default + 1 if default < max_choice else ""

        while True:
            prompt = f"{Spacing.INDENT}Pilih [1-{max_choice}"
            if default_display:
                prompt += f", default {default_display}"
            prompt += "]"
            if allow_back:
                prompt += " (0=kembali)"
            prompt += ": "

            try:
                val = Prompt._read_line(prompt).strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if allow_back and val in ("0", "b", "kembali", "back"):
                return None

            if not val and default_display:
                return default

            try:
                choice = int(val)
                if min_choice <= choice <= max_choice:
                    return choice - 1
                Message.print_warning(f"Pilih antara {min_choice} dan {max_choice}")
            except ValueError:
                Message.print_warning("Masukkan nomor yang valid")

    @staticmethod
    def confirm(label: str, default: bool = False, allow_back: bool = True) -> Optional[bool]:
        """Yes/No confirmation prompt."""
        default_hint = "Y/n" if default else "y/N"
        back_hint = " (b/kembali untuk batal)" if allow_back else ""
        full_prompt = f"{Spacing.INDENT}{Color.cyan(label)} [{default_hint}]{back_hint}: "

        while True:
            try:
                val = Prompt._read_line(full_prompt).strip().lower()
            except (KeyboardInterrupt, EOFError):
                return None

            if allow_back and val in ("b", "kembali", "back"):
                return None

            if not val:
                return default
            if val in ("y", "ya", "yes"):
                return True
            if val in ("n", "tidak", "no"):
                return False
            Message.print_warning("Masukkan y/ya/yes atau n/tidak/no")

    @staticmethod
    def pause(label: str = "Tekan Enter untuk lanjutkan...") -> None:
        """Wait for user to press Enter."""
        Prompt._read_line(f"{Spacing.INDENT}{Color.dim(label)}")
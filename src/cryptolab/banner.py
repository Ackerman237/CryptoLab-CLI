"""Banner and terminal utilities for CryptoLab UI."""

import shutil
import sys
from typing import Optional

# ============================================================
# Logo definitions (SVG-style block pixel font - CRYPTOLAB)
# ============================================================

# CRYPTOLAB in 5x7 block font, clean and crisp
LOGO_LARGE = """\
██████  ██████  ██    ██ ██████  ████████  ██████  ██       █████  ██████
██      ██   ██  ██  ██  ██   ██ ██    ██ ██   ██ ██      ██   ██ ██   ██
██      ██████    ████   ██████  ██    ██ ██████  ██      ███████ ██████
██      ██   ██    ██    ██      ██    ██ ██   ██ ██      ██   ██ ██   ██
 ██████ ██   ██    ██    ██      ██     ██████  ███████ ██   ██ ██   ██"""

LOGO_MEDIUM = """\
██████ ██████ ██  ██ ██████ ████████ ██████ ██    █████ ██████
██     ██  ██ ██ ██  ██  ██ ██    ██ ██     ██   ██ ██   ██
██     ██████ ████   ██████ ██    ██ █████  ██   ███████ ██████
██     ██  ██ ██ ██  ██     ██    ██ ██     ██   ██ ██   ██
 ██████ ██  ██ ██  ██ ██     ██     ██████ ███████ ██ ██   ██"""

LOGO_SMALL = """\
██████ ██████ ██  ██ ██████ ████████ ██████
██     ██  ██ ██ ██  ██  ██ ██    ██ ██   
██     ██████ ████   ██████ ██    ██ █████ 
██     ██  ██ ██ ██  ██     ██    ██ ██   
 ██████ ██  ██ ██  ██ ██     ██     ██████"""

LOGO_TINY = "CRYPTOLAB"

# SVG path data for reference (5x7 pixel font for "CRYPTOLAB")
# Each letter is 5x7 blocks, total width ~53 chars, height 5 lines
# The SVG provided uses crispEdges for pixel-perfect rendering

# ============================================================
# Color constants
# ============================================================
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
WHITE = "\033[97m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
YELLOW = "\033[33m"

def paint(text: str, style: str = "") -> str:
    """Apply ANSI style to text."""
    if not text:
        return ""
    return f"{style}{text}{RESET}"


def term_width(default: int = 80) -> int:
    """Get terminal width."""
    return shutil.get_terminal_size((default, 24)).columns


def term_height(default: int = 24) -> int:
    """Get terminal height."""
    return shutil.get_terminal_size((80, default)).lines


def _block_width(text: str) -> int:
    """Get max line width of a multi-line string."""
    return max(len(line) for line in text.splitlines())


def center_block(text: str, width: int, offset: int = 0) -> str:
    """Center a multi-line block within width, with optional offset."""
    lines = text.splitlines()
    return "\n".join(line.center(width) for line in lines)


def pick_logo(width: int, max_rows: int = 99) -> str:
    """Pick largest logo that fits width AND height."""
    for logo in (LOGO_LARGE, LOGO_MEDIUM, LOGO_SMALL):
        if _block_width(logo) <= width and len(logo.splitlines()) <= max_rows:
            return logo
    return LOGO_TINY


def render_header(subtitle: str = "", max_logo_rows: int = 99) -> str:
    """Render header with logo, blank line, and subtitle."""
    w = term_width()
    logo = paint(center_block(pick_logo(w, max_logo_rows), w), WHITE)
    if subtitle:
        if len(subtitle) > w:
            subtitle = subtitle.split(" · ")[0]
        if len(subtitle) > w:
            subtitle = subtitle[: max(w - 1, 0)] + "…"
        sub = paint(subtitle.center(w), DIM)
        return "\n".join(["", logo, "", sub])
    return "\n".join(["", logo])


def _fit_hints(hints, width: int, gap: int = 3):
    """Fit hints to terminal width by dropping from end."""
    chosen = list(hints)
    while chosen:
        if len((" " * gap).join(f"{k} {l}" for k, l in chosen)) <= width - 2:
            return chosen
        chosen.pop()
    return []


def render_footer(hints, gap: int = 3) -> str:
    """Render footer with thin rule and centered hints."""
    w = term_width()
    chosen = _fit_hints(hints, w, gap)
    plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
    styled = (" " * gap).join(f"{paint(k, BOLD + WHITE)} {paint(l, DIM)}" for k, l in chosen)
    rule = paint(" " * 2 + "─" * max(w - 4, 0), DIM)
    return rule + "\n" + " " * max((w - len(plain)) // 2, 0) + styled


def _clip(text: str, width: int) -> str:
    """Clip text to width with ellipsis."""
    return text if len(text) <= width else text[: max(width - 1, 0)] + "…"


# ============================================================
# Security Warnings
# ============================================================

def warn_weak_hash(algorithm: str) -> str:
    """Return warning message for weak hash algorithms."""
    warnings = {
        "MD5": "PERINGATAN: MD5 adalah hash lemah (collision attacks praktis). JANGAN gunakan untuk keamanan.",
        "SHA1": "PERINGATAN: SHA-1 adalah hash lemah (collision attacks praktis). JANGAN gunakan untuk keamanan.",
    }
    return warnings.get(algorithm.upper(), "")


def warn_ecb_mode() -> str:
    """Return warning for ECB mode."""
    return "PERINGATAN: Mode ECB tidak aman untuk data >1 blok (pola plaintext terlihat). Gunakan CBC/GCM."


def warn_rc2() -> str:
    """Return warning for RC2 cipher."""
    return "PERINGATAN: RC2/ARC2 adalah cipher legacy (deprecated 2015). Gunakan AES untuk sistem baru."


def warn_rsa_pkcs1v15() -> str:
    """Return warning for RSA PKCS#1 v1.5."""
    return "PERINGATAN: PKCS#1 v1.5 rentan terhadap padding oracle. Gunakan OAEP (encrypt) / PSS (sign)."


def print_warning(message: str) -> None:
    """Print a formatted warning message."""
    if message:
        sys.stdout.write(f"{YELLOW}{message}{RESET}\n")
        sys.stdout.flush()


# ============================================================
# Hints
# ============================================================
HINTS_MAIN = [("↑↓", "navigasi"), ("enter", "pilih"), ("q", "keluar"), ("?", "bantuan")]
HINTS_SUB = [("↑↓", "navigasi"), ("enter", "pilih"), ("esc", "kembali"), ("q", "keluar"), ("?", "bantuan")]

# ============================================================
# Terminal control
# ============================================================
def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def save_cursor():
    sys.stdout.write("\033[s")
    sys.stdout.flush()


def restore_cursor():
    sys.stdout.write("\033[u")
    sys.stdout.flush()


def clear_from_cursor():
    sys.stdout.write("\033[J")
    sys.stdout.flush()
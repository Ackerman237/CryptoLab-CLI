"""Banner and terminal utilities for CryptoLab UI.

Per padanan panduan 'PROMPT_rombak_ui_cryptolab.md' bagian 6.1:
- ``vlen`` menghitung panjang terlihat (tanpa kode ANSI).
- ``center_block`` memusatkan blok logo SEBAGAI SATU BLOK (padding sama untuk
  semua baris), bukan memusatkan tiap baris sendiri-sendiri.
- ``pick_logo`` memilih logo terbesar yang muat di lebar DAN tinggi.
- ``render_header`` mengembalikan header dengan logo + subtitle terpusat.
- Konstanta ``APP_VERSION`` dan ``HEADER_SUBTITLE`` adalah satu sumber kebenaran.
"""

import re
import shutil
import sys
from typing import Optional

# ============================================================
# Versi aplikasi (satu sumber kebenaran)
# ============================================================
# Dipilih dari pyproject.toml (= 1.2.0) dan src/cryptolab/__init__.py (= 1.2.0).
APP_VERSION = "1.2.0"
HEADER_SUBTITLE = f"CRYPTOLAB CLI v{APP_VERSION} · TOOLKIT KRIPTOGRAFI & ENCODING"

# ============================================================
# Logo definitions (block pixel font - CRYPTOLAB)
# ============================================================
# Font blok 5 baris; huruf CRPTOLAB dari matriks 6 kolom (5 glyph + 1 jarak)
# sehingga SEMUA baris punya lebar identik - tanpa ini tepi kanan bergerigi.
# Huruf dihasilkan dari matriks di komentar (bukan digambar manual).

# CRYPTOLAB (9 huruf, lebar 62)
LOGO_LARGE = """\
██████ ██████ ██  ██ ██████ ██████ ██████ ██      ████  █████ 
██     ██  ██  ████  ██  ██   ██   ██  ██ ██     ██  ██ ██  ██
██     ██████   ██   ██████   ██   ██  ██ ██     ██████ █████ 
██     ██  ██   ██   ██       ██   ██  ██ ██     ██  ██ ██  ██
██████ ██  ██   ██   ██       ██   ██████ ██████ ██  ██ █████ """

# CRYPTO (6 huruf, lebar 41)
LOGO_MEDIUM = """\
██████ ██████ ██  ██ ██████ ██████ ██████
██     ██  ██  ████  ██  ██   ██   ██  ██
██     ██████   ██   ██████   ██   ██  ██
██     ██  ██   ██   ██       ██   ██  ██
██████ ██  ██   ██   ██       ██   ██████"""

# CRYPT (5 huruf, lebar 34)
LOGO_SMALL = """\
██████ ██████ ██  ██ ██████ ██████
██     ██  ██  ████  ██  ██   ██  
██     ██████   ██   ██████   ██  
██     ██  ██   ██   ██       ██  
██████ ██  ██   ██   ██       ██  """

LOGO_TINY = "CRYPTOLAB"

# Versi ASCII polos: tidak memakai karakter blok U+2588, sehingga selalu rapi
# di terminal/konsol yang tidak punya glyph blok (mis. Windows Legacy Console).
LOGO_ASCII = """\
  ___ ___ __   __ ___ ___ _____ ___  _    ___ ___
 / __| _ \\ \\ / /| _ \\_ _|_   _/ _ \\| |  / _ \\ _ )
| (__|   / \\ V / |  _/| |  | || (_) | |_| (_) | _ \\
 \\___|_|_\\  |_|  |_| |___| |_| \\___/|____\\___/|___/"""

LOGO_ASCII_MEDIUM = """\
  ___ ___ __   __ ___ ___ _____
 / __| _ \\ \\ / /| _ \\_ _|_   _|
| (__|   / \\ V / |  _/| |  | |
 \\___|_|_\\  |_|  |_| |___| |_|"""

# Karakter blok dianggap tampil rapi hanya pada lingkungan yang mendukungnya.
# Set CRYPTOLAB_ASCII_LOGO=1 (atau pakai --ascii-logo) untuk logo ASCII polos.
import os as _os

_ASCII_ONLY = _os.environ.get("CRYPTOLAB_ASCII_LOGO", "").strip() not in ("", "0", "false", "False")


def set_ascii_logo(enabled: bool = True) -> None:
    """Paksa logo ASCII polos (untuk terminal tanpa glyph blok U+2588)."""
    global _ASCII_ONLY
    _ASCII_ONLY = bool(enabled)


def ascii_logo_enabled() -> bool:
    """Apakah logo ASCII polos sedang dipaksa."""
    return _ASCII_ONLY

# SVG path data for reference (5x7 pixel font for "CRYPTOLAB")
# Each letter is 5x7 blocks, total width ~53 chars, height 5 lines
# The SVG provided uses crispEdges for pixel-perfect rendering

# ============================================================
# Color constants
# ============================================================
# Regex untuk melucuti kode ANSI saat menghitung panjang terlihat.
_ANSI = re.compile(r"\033\[[0-9;?]*[A-Za-z]")

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


def vlen(s: str) -> int:
    """Panjang teks yang terlihat (tanpa kode ANSI)."""
    return len(_ANSI.sub("", s))


def term_width(default: int = 80) -> int:
    """Get terminal width."""
    return shutil.get_terminal_size((default, 24)).columns


def term_height(default: int = 24) -> int:
    """Get terminal height."""
    return shutil.get_terminal_size((80, default)).lines


def _block_width(text: str) -> int:
    """Get max *visible* line width of a multi-line string (ANSI stripped)."""
    return max((vlen(line) for line in text.splitlines()), default=0)


def center_block(text: str, width: int, offset: int = 0) -> str:
    """Pusatkan blok logo SEBAGAI SATU BLOK.

    Padding kiri dihitung dari tepi TERJAUH kiri glyph (bukan dari spasi
    bawaan tiap baris), lalu setiap baris digeser dengan padding yang sama.
    Dengan begitu tepi kiri glyph sejajar untuk semua baris walaupun glyph
    seperti Y/T memakai spasi di kolom pertamanya (miring ke kanan) dan
    huruf lain tidak.
    """
    lines = text.splitlines()
    bw = max((vlen(l) for l in lines), default=0)
    # Leading minimum di seluruh blok: hanya spasi yang dipakai SEMUA baris.
    common = min((len(l) - len(l.lstrip(" ")) for l in lines if l.strip()), default=0)
    pad = " " * max((width - bw) // 2 - common, 0)
    return "\n".join(pad + l for l in lines)


def pick_logo(width: int, max_rows: int = 99) -> str:
    """Pick largest logo that fits width AND height."""
    order = (
        (LOGO_ASCII, LOGO_ASCII_MEDIUM, LOGO_TINY)
        if ascii_logo_enabled()
        else (LOGO_LARGE, LOGO_MEDIUM, LOGO_SMALL, LOGO_ASCII, LOGO_ASCII_MEDIUM, LOGO_TINY)
    )
    for logo in order:
        if _block_width(logo) <= width and len(logo.splitlines()) <= max_rows:
            return logo
    return LOGO_TINY


def render_header(subtitle: str = "", max_logo_rows: int = 99) -> str:
    """Render header with logo, blank line, and subtitle.

    Garis pemisah tidak dicetak di sini; garisnya cukup di footer agar header
    tetap ringkas dan ruang hasil lebih luas.
    """
    w = term_width()
    logo = paint(center_block(pick_logo(w, max_logo_rows), w), WHITE)
    if subtitle:
        if vlen(subtitle) > w:
            # terlalu lebar: buang bagian setelah " · "
            subtitle = subtitle.split(" · ")[0]
        if vlen(subtitle) > w:
            subtitle = subtitle[: max(w - 1, 0)] + "…"
        sub = paint(subtitle.center(w), DIM)
        return "\n".join(["", logo, "", sub])
    return "\n".join(["", logo])


def _fit_hints(hints, width: int, gap: int = 3):
    """Fit hints to terminal width by dropping from end. Uses vlen for accuracy."""
    chosen = list(hints)
    while chosen:
        plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
        if vlen(plain) <= width - 2:
            return chosen
        chosen.pop()
    return []


def render_footer(hints, gap: int = 3) -> str:
    """Render footer with thin rule and centered hints.

    Menggunakan vlen() untuk menghitung panjang teks plain (tanpa ANSI) agar
    garis dan hint selalu sejajar di tengah.
    """
    w = term_width()
    chosen = _fit_hints(hints, w, gap)
    plain = (" " * gap).join(f"{k} {l}" for k, l in chosen)
    styled = (" " * gap).join(f"{paint(k, BOLD + WHITE)} {paint(l, DIM)}" for k, l in chosen)
    rule = paint(" " * 2 + "─" * max(w - 4, 0), DIM)
    return rule + "\n" + " " * max((w - vlen(plain)) // 2, 0) + styled


def _clip(text: str, width: int) -> str:
    """Clip text to visible width with ellipsis."""
    return text if vlen(text) <= width else text[: max(width - 1, 0)] + "…"


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
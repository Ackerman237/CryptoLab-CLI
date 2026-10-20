"""Interactive Package - Terminal Interface for CryptoLab.

Perombakan UI sesuai panduan 'PROMPT_rombak_ui_cryptolab.md' bagian 6.4:
- Menu utama 3-elemen: (label_pendek, aksi, keterangan).
- ``menu_lines`` dan ``draw_menu`` memakai ``render_menu`` + ``render_footer``
  dari ``ui.ui`` dan ``render_header`` dari ``banner``.
- ``run_interactive_menu`` memakai ``read_key`` dengan normalisasi tombol
  dari ``interactive.navigation``, layar alternatif (\033[?1049h), kursor
  disembunyikan, dan dipulihkan di ``finally``.
- Item yang berupa fungsi fitur (ctx API) dipanggil via ``run_action`` dari
  ``flow``; item lama (handler ``handle_*`` tanpa ctx) dipanggil langsung
  untuk backward compatibility selama masa migrasi.
"""

import sys

from cryptolab.banner import (
    render_header, term_width, term_height, vlen, paint, WHITE, DIM,
    HEADER_SUBTITLE, APP_VERSION,
)
from cryptolab.ui.ui import render_menu, render_footer, HINTS_MAIN, HINTS_SUB
from cryptolab.flow import run_action
from cryptolab.interactive.navigation import read_key

# Re-export UI symbols for backward compatibility
from cryptolab.ui.widgets.menu import Menu, navigation_menu
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
# Import ctx-based handlers (API baru)
from cryptolab.interactive.handlers.ctx_encoding import fn_base64, fn_hex, fn_binary
from cryptolab.interactive.handlers.ctx_analysis import fn_auto
from cryptolab.interactive.handlers.ctx_history import fn_history
from cryptolab.interactive.handlers.ctx_classical import fn_caesar, fn_vigenere
from cryptolab.interactive.handlers.ctx_symmetric import fn_des, fn_aes, fn_rc2
from cryptolab.interactive.handlers.ctx_hashing import fn_hash
from cryptolab.interactive.handlers.ctx_asymmetric import fn_rsa, fn_dh

# Konstanta hint di-reexport dari ui.ui agar satu sumber kebenaran.
__all__ = [
    "get_main_menu_labels",
    "get_main_menu_handlers",
    "get_header_subtitle",
    "navigation_menu",
    "read_key",
    "Menu",
    "render_menu",
    "menu_lines",
    "draw_menu",
    "screen",
    "render_header",
    "term_width",
    "term_height",
    "HEADER_SUBTITLE",
    "HINTS_MAIN",
    "HINTS_SUB",
    "run_interactive_menu",
    "save_result_prompt",
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


# ============================================================
# Menu container (backward compatibility)
# ============================================================

class Menu:
    """Simple menu container with title and items (3-elemen: label, aksi, keterangan)."""

    def __init__(self, title: str, items: list):
        self.title = title
        self.items = items


def _clip(text: str, width: int) -> str:
    """Clip text to visible width with ellipsis."""
    return text if vlen(text) <= width else text[: max(width - 1, 0)] + "…"


# ============================================================
# save_result_prompt (backward compatibility)
# ============================================================

def save_result_prompt(content: str, default_filename: str = "hasil_cryptolab.txt") -> None:
    """Prompt user to optionally save text content to a file."""
    from pathlib import Path
    try:
        choice = input(f"\n  Simpan hasil ke file? (y/n) [n]: ").lower()
        if choice in ("y", "ya", "yes"):
            fn_input = input(f"  Nama file [{default_filename}]: ")
            filename = fn_input or default_filename
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")
            print(f"  [OK] Hasil berhasil disimpan ke: {filepath.resolve()}")
    except Exception as err:
        print(f"  [!] Gagal menyimpan file: {err}")


# ============================================================
# Menu rendering (menu_lines, draw_menu, screen)
# ============================================================

def menu_lines(menu, sel, depth):
    """Bangun seluruh baris layar menu: header + judul + menu + footer.

    Total baris dipotong ke tinggi terminal. Logo mengecil otomatis bila
    tinggi tidak cukup (pick_logo dengan max_logo_rows). Footer selalu
    dijamin terlihat dengan menyisakan ruang 2 baris (garis + hint).
    """
    h = term_height()
    labels = [it[0] for it in menu.items]
    descs = [it[2] if len(it) > 2 else "" for it in menu.items]
    hints = HINTS_SUB if depth > 0 else HINTS_MAIN

    # Footer = 2 baris (garis + hint). Judul = 3 baris (kosong + judul + kosong).
    # Sisakan ruang untuk footer dengan mengurangi avail_rows.
    footer_rows = 2  # render_footer menghasilkan garis + hint = 2 baris
    title_rows = 3   # "", title_line, ""

    # Logo mengecil: prioritaskan ruang menu dan footer.
    # Sisakan minimal 1 baris untuk logo. Bila tinggi sangat terbatas,
    # logo otomatis menjadi LOGO_TINY (1 baris) agar menu tetap terlihat.
    # Reservasi: footer 2 baris, judul 3 baris, baris kosong 2, menu minimal 3.
    reserved = title_rows + footer_rows + 2  # judul + footer + baris kosong
    menu_min = 3  # minimal 3 baris menu (1 item + 2 scroll indicator)
    want_menu = min(len(labels), max(h - reserved - 5, menu_min))
    logo_rows = max(h - reserved - want_menu, 1)
    # Bila tinggi terlalu kecil untuk logo 5-baris, paksa logo mengecil.
    if h <= 16:
        logo_rows = min(logo_rows, max(h - reserved - menu_min, 1))
    header = render_header(HEADER_SUBTITLE, max_logo_rows=logo_rows).split("\n")

    # avail = tinggi - header - judul - footer - baris kosong
    avail = max(h - len(header) - title_rows - footer_rows - 2, 1)
    body = render_menu(labels, sel, descs, avail_rows=avail)
    w = term_width()
    title_line = paint("Menu Utama".center(w) if menu.title == "Menu Utama" else menu.title.center(w), DIM)
    footer = render_footer(hints)
    lines = header + ["", title_line, ""] + body + ["", footer]
    # Pastikan footer selalu di baris terakhir: potong ke h, tapi selalu sertakan footer.
    if len(lines) > h:
        # Sisakan 2 baris terakhir untuk footer.
        lines = lines[:h - footer_rows] + lines[-footer_rows:]
    return lines[:h]


def draw_menu(menu, sel, depth, full_clear):
    """Gambar menu ke terminal via ``screen``."""
    screen(menu_lines(menu, sel, depth), full_clear)


def screen(lines, full_clear: bool):
    """Render lines to terminal.

    - Memotong ke tinggi terminal.
    - Tidak mencetak newline di baris terakhir (mencegah scroll).
    - Menghapus sisa baris dengan ``\\033[K`` dan sisa layar dengan ``\\033[J``.
    """
    h = term_height()
    out_lines = lines[:h]
    parts = []
    if full_clear:
        parts.append("\033[2J\033[H")
    else:
        parts.append("\033[H")
    for i, line in enumerate(out_lines):
        if i < len(out_lines) - 1:
            parts.append(line + "\n")
        else:
            # Baris terakhir: tidak ada newline (mencegah scroll).
            parts.append(line)
    parts.append("\033[J")
    sys.stdout.write("".join(parts))
    sys.stdout.flush()


# ============================================================
# Menu definitions
# ============================================================

# Sentinel untuk item "Keluar".
def _exit_action():
    """Sentinel: item Keluar memicu return dari loop menu."""
    return "exit"


# Menu utama: (label_pendek, aksi, keterangan)
# Aksi adalah fungsi ctx (fn(ctx) -> Result): dipanggil via run_action.
# Handler lama (handle_*) tetap di-reexport untuk backward compatibility.
_MAIN_MENU = Menu("Menu Utama", [
    ("Auto Analyze",       fn_auto,     "Deteksi otomatis jenis cipher / encoding dari teks"),
    ("Caesar Cipher",      fn_caesar,   "Cipher klasik: geser huruf"),
    ("Vigenere Cipher",    fn_vigenere, "Cipher klasik: kunci berulang"),
    ("DES",                fn_des,      "Data Encryption Standard · 64 bit"),
    ("AES",                fn_aes,      "Advanced Encryption Standard · 128 bit"),
    ("RC2",                fn_rc2,      "ARC2 · legacy 64 bit"),
    ("Hashing & Password", fn_hash,     "MD5, SHA, HMAC, PBKDF2, Bcrypt"),
    ("RSA",                fn_rsa,      "KeyGen, Encrypt, Decrypt, Sign, Verify"),
    ("Diffie-Hellman",     fn_dh,       "Pertukaran kunci (DHKE)"),
    ("Base64",             fn_base64,   "Encode / decode Base64"),
    ("Hex",                fn_hex,      "Encode / decode Hex"),
    ("Binary",             fn_binary,   "Encode / decode Binary"),
    ("Riwayat",            fn_history,  "Lihat riwayat operasi"),
    ("Keluar",             _exit_action, "Tutup aplikasi"),
])


# Backward compatibility: expose labels dan handlers dari menu 3-elemen.
MAIN_LABELS = [it[0] for it in _MAIN_MENU.items]
MAIN_MENU_LABELS = MAIN_LABELS
MAIN_MENU_HANDLERS = [it[1] for it in _MAIN_MENU.items]


def get_main_menu_labels() -> list:
    """Get the main menu labels."""
    return MAIN_LABELS


def get_main_menu_handlers() -> list:
    """Get the main menu handlers."""
    return MAIN_MENU_HANDLERS


def get_header_subtitle() -> str:
    """Get the header subtitle."""
    return HEADER_SUBTITLE


# ============================================================
# Main loop
# ============================================================

def _is_ctx_fn(fn):
    """Cek apakah fn adalah fungsi ctx (menerima ctx, mengembalikan Result).

    Fungsi ctx ditandai dengan atribut ``_ctx_fn = True`` yang dipasang
    di file ctx_*.py.
    """
    return getattr(fn, "_ctx_fn", False)


def run_interactive_menu() -> None:
    """Run the interactive menu loop.

    - Layar alternatif (\033[?1049h) mencegah tumpukan output di scrollback.
    - Kursor disembunyikan selama menu dan dipulihkan di finally.
    - Navigasi ↑↓ dengan wrap-around, enter memilih, q keluar, esc kembali.
    - Item fungsi ctx dipanggil via run_action; handler lama dipanggil langsung.
    """
    from cryptolab.ui.layout import alt_screen_enter, alt_screen_exit
    from cryptolab.banner import hide_cursor, show_cursor

    menu = _MAIN_MENU
    selected = 0
    n = len(menu.items)

    # Hanya gunakan layar alternatif bila stdout adalah TTY.
    use_alt_screen = bool(getattr(sys.stdout, "isatty", lambda: False)())

    if use_alt_screen:
        alt_screen_enter()

    hide_cursor()
    try:
        while True:
            draw_menu(menu, selected, 0, True)

            key = read_key()
            if key is None:
                continue

            if key == "up":
                selected = (selected - 1) % n
            elif key == "down":
                selected = (selected + 1) % n
            elif key == "home":
                selected = 0
            elif key == "end":
                selected = n - 1
            elif key == "enter":
                label, target = menu.items[selected][:2]
                if target is _exit_action or target == _exit_action:
                    return
                # Panggil fitur: kursor tampil dulu, lalu sembunyi lagi setelah.
                show_cursor()
                try:
                    if _is_ctx_fn(target):
                        result = run_action(label, target, read_key)
                        if result == "quit":
                            return
                    else:
                        # Handler lama: panggil langsung.
                        target()
                except KeyboardInterrupt:
                    pass
                finally:
                    hide_cursor()
                # Gambar ulang menu setelah kembali dari aksi.
                draw_menu(menu, selected, 0, True)
            elif key == "q":
                return
            elif key == "?":
                # Bantuan: untuk sekarang no-op (dapat dikembangkan).
                pass
            elif key == "esc":
                # Esc di menu utama: tidak melakukan apa-apa (tidak crash).
                pass
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        if use_alt_screen:
            alt_screen_exit()
        # Pesan perpisahan (pulihkan perilaku menu lama).
        print("\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
        sys.stdout.flush()
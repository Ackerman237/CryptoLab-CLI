"""Tahap 2 - menu tab kategori (upgrade-spec.md).

Menu baru tambahan di atas menu lama (bukan pengganti):
- Tab kategori: ◀ ▶ wrap-around, angka 1..N lompat langsung ke kategori.
- Daftar algoritma: ▲ ▼ wrap-around, Enter memilih, Q / Esc keluar.
- Tag ``baru`` (hijau) dan ``⚠ usang`` (kuning) mengikuti tanda yang ada.
- Mode sempit: bila seluruh tab tidak muat, hanya tab aktif yang tampil.
- Karakter kotak memakai ``Symbol`` (fallback ASCII otomatis dari ui.theme).
- Fallback ke menu lama bila stdin/stdout bukan TTY (lihat run_interactive_menu).

Item tanpa handler (``target=None``) adalah mode baru Tahap 3: tampil dengan
tag ``baru``, tapi Enter hanya menampilkan status "belum tersedia".
"""

from cryptolab.banner import (
    paint, vlen, term_width, BOLD, DIM, GREEN, CYAN, YELLOW,
)
from cryptolab.ui.theme import Symbol

from cryptolab.interactive.handlers.ctx_encoding import fn_base64, fn_hex, fn_binary
from cryptolab.interactive.handlers.ctx_analysis import fn_auto
from cryptolab.interactive.handlers.ctx_history import fn_history
from cryptolab.interactive.handlers.ctx_classical import fn_caesar, fn_vigenere
from cryptolab.interactive.handlers.ctx_symmetric import fn_des, fn_aes, fn_rc2
from cryptolab.interactive.handlers.ctx_hashing import fn_hash
from cryptolab.interactive.handlers.ctx_asymmetric import fn_rsa, fn_dh

__all__ = ["CATEGORIES", "tab_menu_lines", "run_tab_menu"]


# (kategori, [(label, target, tag)])  -- tag: "" | "baru" | "usang".
# Label item dipertahankan persis seperti menu utama lama.
# target None = mode baru Tahap 3 (belum punya handler).
CATEGORIES = [
    ("Klasik", [
        ("Caesar Cipher", fn_caesar, ""),
        ("Vigenere Cipher", fn_vigenere, ""),
    ]),
    ("Simetris", [
        ("AES", fn_aes, ""),
        ("AES-GCM", None, "baru"),
        ("DES", fn_des, "usang"),
        ("RC2", fn_rc2, "usang"),
    ]),
    ("Asimetris", [
        ("RSA", fn_rsa, ""),
        ("Diffie-Hellman", fn_dh, ""),
        ("Digital Signature", None, "baru"),
    ]),
    ("Hash", [
        ("Hashing & Password", fn_hash, ""),
        ("SHA-3", None, "baru"),
        ("SHA-512", None, "baru"),
        ("HMAC-SHA-256", None, "baru"),
        ("Argon2id / bcrypt", None, "baru"),
    ]),
    ("Encoding", [
        ("Base64", fn_base64, ""),
        ("Hex", fn_hex, ""),
        ("Binary", fn_binary, ""),
    ]),
    ("Utilitas", [
        ("Auto Analyze", fn_auto, ""),
        ("Riwayat", fn_history, ""),
    ]),
]

HINT_TAB = (
    f"{Symbol.ARROW_LEFT} {Symbol.ARROW_RIGHT} kategori   "
    f"{Symbol.ARROW_UP} {Symbol.ARROW_DOWN} algoritma   Enter pilih   Q keluar"
)


def _center(painted: str, width: int) -> str:
    """Pusatkan satu baris (lehat terlihat, abaikan kode ANSI)."""
    return " " * max((width - vlen(painted)) // 2, 0) + painted


def _rule(width: int) -> str:
    return paint("  " + Symbol.BOX_H * max(width - 4, 0), DIM)


def _tab_bar(names, ci: int, width: int) -> str:
    """Baris tab: penuh bila muat, mode sempit bila tidak."""
    inner = Symbol.BOX_V.join(
        paint(f"[{name}]", BOLD + CYAN) if i == ci else paint(f" {name} ", DIM)
        for i, name in enumerate(names)
    )
    bar = f"  {Symbol.ARROW_LEFT}  {inner}  {Symbol.ARROW_RIGHT}  "
    if vlen(bar) <= width - 2:
        return _center(bar, width)
    # Mode sempit: hanya tab aktif, sesuai spesifikasi.
    narrow = (
        f"  {Symbol.ARROW_LEFT} {paint(f'[{names[ci]}]', BOLD + CYAN)} "
        f"({ci + 1}/{len(names)}) {Symbol.ARROW_RIGHT}  "
    )
    return _center(narrow, width)


def tab_menu_lines(ci: int, ai: int, status: str = "") -> list:
    """Bangun seluruh baris layar menu tab: tab + daftar algoritma + footer."""
    width = term_width()
    names = [name for name, _ in CATEGORIES]
    items = CATEGORIES[ci][1]

    lines = ["", _tab_bar(names, ci, width), _rule(width), ""]

    label_width = max(len(label) for _, group in CATEGORIES for label, _, _ in group)
    pad = max((width - (4 + label_width)) // 2, 0)
    for i, (label, _target, tag) in enumerate(items):
        pointer = f"{Symbol.POINTER} " if i == ai else "  "
        body = paint(f"{pointer}{label}", BOLD) if i == ai else paint(f"{pointer}{label}", DIM)
        if tag == "usang":
            body += "   " + paint(f"{Symbol.WARNING} usang", YELLOW)
        elif tag == "baru":
            body += "   " + paint("baru", GREEN)
        lines.append(" " * pad + body)

    lines += ["", _rule(width)]
    if status:
        lines.append(_center(paint(status, YELLOW), width))
    lines.append(_center(paint(HINT_TAB, DIM), width))
    return lines


def run_tab_menu(dispatch, read_key) -> None:
    """Loop menu tab kategori.

    Args:
        dispatch: dipanggil ``dispatch(label, target)`` saat Enter; nilai
            truthy berarti aplikasi harus keluar (mis. hasil "quit").
        read_key: fungsi baca tombol (``interactive.navigation.read_key``).
    """
    from cryptolab.interactive import screen

    ci, ai = 0, 0
    status = ""
    while True:
        screen(tab_menu_lines(ci, ai, status), full_clear=True)

        key = read_key()
        status = ""
        if key is None:
            continue

        items = CATEGORIES[ci][1]
        if key == "left":
            ci = (ci - 1) % len(CATEGORIES)
            ai = 0
        elif key == "right":
            ci = (ci + 1) % len(CATEGORIES)
            ai = 0
        elif key == "up":
            ai = (ai - 1) % len(items)
        elif key == "down":
            ai = (ai + 1) % len(items)
        elif key.isdigit() and 1 <= int(key) <= len(CATEGORIES):
            ci, ai = int(key) - 1, 0
        elif key == "enter":
            label, target = items[ai][:2]
            if target is None:
                status = f"{label} belum tersedia - mode baru ditambahkan di Tahap 3."
            elif dispatch(label, target):
                return
        elif key in ("q", "esc"):
            return
        # Tombol lain (home/end/pgup/...) diabaikan.

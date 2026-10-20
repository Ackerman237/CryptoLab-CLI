"""Tahap 2 - menu tab kategori (upgrade-spec.md).

Menu baru tambahan di atas menu lama (bukan pengganti):
- Tab kategori: ◀ ▶ wrap-around, angka 1..N lompat langsung ke kategori.
- Daftar algoritma: ▲ ▼ wrap-around, Enter memilih, Q / Esc keluar.
- Tag ``baru`` (hijau) dan ``⚠ usang`` (kuning) mengikuti tanda yang ada.
- Mode sempit: bila seluruh tab tidak muat, hanya tab aktif yang tampil.
- Karakter kotak memakai ``Symbol`` (fallback ASCII otomatis dari ui.theme).
- Fallback ke menu lama bila stdin/stdout bukan TTY (lihat run_interactive_menu).
- Semua item sudah punya handler (Tahap 3 selesai). Kategori "Hash" memuat
  Argon2id / bcrypt: Argon2id butuh dependency baru (argon2-cffi), jadi opsi
  yang tersedia adalah bcrypt (bila paket terpasang) atau PBKDF2-SHA256 stdlib.
"""
from cryptolab.banner import (
    paint, vlen, term_width, term_height, BOLD, DIM, GREEN, CYAN, YELLOW,
    WHITE, GREY, render_header, format_subtitle,
)
from cryptolab.ui.theme import Symbol

from cryptolab.interactive.handlers.ctx_encoding import fn_base64, fn_hex, fn_binary
from cryptolab.interactive.handlers.ctx_analysis import fn_auto
from cryptolab.interactive.handlers.ctx_history import fn_history
from cryptolab.interactive.handlers.ctx_classical import fn_caesar, fn_vigenere
from cryptolab.interactive.handlers.ctx_symmetric import fn_des, fn_aes, fn_aes_gcm, fn_rc2
from cryptolab.interactive.handlers.ctx_hashing import (
    fn_hash,
    fn_sha3,
    fn_sha512,
    fn_hmac256,
    fn_keygen,
    fn_password,
)
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
        ("AES-GCM", fn_aes_gcm, "baru"),
        ("DES", fn_des, "usang"),
        ("RC2", fn_rc2, "usang"),
    ]),
    ("Asimetris", [
        ("RSA", fn_rsa, ""),
        ("Diffie-Hellman", fn_dh, ""),
        # RSA-PSS (rsa_sign/rsa_verify) sudah ada di core; fn_rsa memuat Sign/Verify.
        ("Digital Signature", fn_rsa, "baru"),
    ]),
    ("Hash", [
        ("Hashing & Password", fn_hash, ""),
        ("SHA-3", fn_sha3, "baru"),
        ("SHA-512", fn_sha512, "baru"),
        ("HMAC-SHA-256", fn_hmac256, "baru"),
        ("Argon2id / bcrypt", fn_password, "baru"),
    ]),
    ("Encoding", [
        ("Base64", fn_base64, ""),
        ("Hex", fn_hex, ""),
        ("Binary", fn_binary, ""),
    ]),
    ("Utilitas", [
        ("Auto Analyze", fn_auto, ""),
        ("Riwayat", fn_history, ""),
        ("Generate Key", fn_keygen, "baru"),
    ]),
]

HINT_TAB = (
    f"{Symbol.ARROW_LEFT} {Symbol.ARROW_RIGHT} kategori   "
    f"{Symbol.ARROW_UP} {Symbol.ARROW_DOWN} algoritma   Enter pilih   Q keluar"
)

# Penjelasan singkat tiap kategori (ditampilkan di bawah daftar algoritma).
CATEGORY_DESC = {
    "Klasik": "cipher klasik berbasis substitusi dan pergeseran",
    "Simetris": "enkripsi satu kunci - cepat, kunci harus dirahasiakan",
    "Asimetris": "pasangan kunci publik/privat untuk enkripsi dan tanda tangan",
    "Hash": "fungsi satu arah untuk integritas, MAC, dan password",
    "Encoding": "konversi representasi data, bukan enkripsi",
    "Utilitas": "analisis otomatis, riwayat, dan pembangkit kunci acak",
}


def _header_lines(width: int, avail_rows: int) -> list:
    """Logo + subtitle versi, mengecil otomatis bila tinggi terminal terbatas.

    ``logo_text`` dipatok ke lebar ini supaya ``render_header`` tidak memanggil
    ``pick_logo`` lagi (pemilihan ukuran sudah dilakukan lewat ``avail_rows``).
    """
    if avail_rows < 1:
        return []
    return render_header(
        format_subtitle(), max_logo_rows=avail_rows
    ).split("\n")


def _center(painted: str, width: int) -> str:
    """Pusatkan satu baris (lehat terlihat, abaikan kode ANSI)."""
    return " " * max((width - vlen(painted)) // 2, 0) + painted


def _rule(width: int) -> str:
    # Pemisah paling samar: hanya pembantu baca, bukan konten.
    return paint("  " + Symbol.BOX_H * max(width - 4, 0), GREY)


def _tab_bar(names, ci: int, width: int) -> str:
    """Baris tab: penuh bila muat, mode sempit bila tidak."""
    inner = Symbol.BOX_V.join(
        paint(f"[{name}]", BOLD + CYAN) if i == ci else paint(f" {name} ", GREY)
        for i, name in enumerate(names)
    )
    bar = f"  {paint(Symbol.ARROW_LEFT, GREY)}  {inner}  {paint(Symbol.ARROW_RIGHT, GREY)}  "
    if vlen(bar) <= width - 2:
        return _center(bar, width)
    # Mode sempit: hanya tab aktif, sesuai spesifikasi.
    narrow = (
        f"  {paint(Symbol.ARROW_LEFT, GREY)} {paint(f'[{names[ci]}]', BOLD + CYAN)} "
        f"({ci + 1}/{len(names)}) {paint(Symbol.ARROW_RIGHT, GREY)}  "
    )
    return _center(narrow, width)


def tab_menu_lines(ci: int, ai: int, status: str = "") -> list:
    """Bangun seluruh baris layar menu tab.

    Susunan: logo + subtitle versi, tab kategori, daftar algoritma,
    penjelasan kategori, lalu footer hint.

    Bila tinggi terminal terbatas, bagian yang dipotong lebih dulu (berurutan):
    baris kosong, penjelasan kategori, logo (mengecil otomatis), dan daftar
    algoritma. Tab kategori + minimal 3 item + footer selalu tampil.
    """
    width = term_width()
    h = term_height()
    names = [name for name, _ in CATEGORIES]
    items = CATEGORIES[ci][1]

    head = [_tab_bar(names, ci, width), _rule(width)]
    desc = CATEGORY_DESC.get(names[ci], "")
    desc_line = _center(paint(desc, GREY), width)
    tail = [_rule(width)]
    if status:
        tail.append(_center(paint(status, YELLOW), width))
    tail.append(_center(paint(HINT_TAB, GREY), width))

    label_width = max(len(label) for _, group in CATEGORIES for label, _, _ in group)
    pad = max((width - (4 + label_width)) // 2, 0)

    def item_line(i, label, tag):
        pointer = f"{Symbol.POINTER} " if i == ai else "  "
        body = paint(f"{pointer}{label}", BOLD + WHITE) if i == ai else paint(f"{pointer}{label}", GREY)
        if tag == "usang":
            body += "   " + paint(f"{Symbol.WARNING} usang", YELLOW)
        elif tag == "baru":
            body += "   " + paint("baru", GREEN)
        return " " * pad + body

    # Baris wajib: 2 head + minimal 3 item + garis + footer (+status bila ada).
    min_items = min(3, len(items))
    reserved = len(head) + min_items + len(tail)
    avail = h - reserved

    # Prioritas saat sempit: item (maks semua) -> logo -> penjelasan.
    show_items = min(len(items), max(avail + 1, min_items))
    left = max(avail - (show_items - min_items), 0)
    logo_rows = min(6, max(left - 2, 0)) if left >= 3 else 0
    show_desc = bool(desc) and (left - logo_rows) >= 1

    def build(with_logo, with_desc):
        out = []
        if with_logo:
            out += _header_lines(width, logo_rows)
            out.append("")
        out += head
        out += [item_line(i, label, tag) for i, (label, _t, tag) in enumerate(items[:show_items])]
        out.append("")
        if with_desc:
            out.append(desc_line)
        return out + tail

    lines = build(bool(logo_rows), show_desc)
    if len(lines) > h:
        # Buang bagian yang tidak wajib sampai muat, footer selalu terlihat.
        lines = build(bool(logo_rows), False)
    while len(lines) > h and show_items > min_items:
        show_items -= 1
        lines = build(bool(logo_rows), False)
    if len(lines) > h:
        lines = build(False, False)
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
            if dispatch(label, target):
                return
        elif key in ("q", "esc"):
            return
        # Tombol lain (home/end/pgup/...) diabaikan.

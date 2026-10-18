"""Interactive Terminal Interface for CryptoLab CLI.

Provides a professional, beginner-friendly menu in Bahasa Indonesia
with clear prompts, input validation, back navigation, and consistent formatting.
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import readchar
from readchar import key as readchar_key

from cryptolab import __version__
from cryptolab.exceptions import (
    CryptoLabError,
    DecodingError,
    InvalidInputError,
    InvalidKeyError,
)
from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.encoding.binary_codec import binary_encode, binary_decode
from cryptolab.symmetric.des import des_encrypt, des_decrypt, des_auto_analyze, DesResult
from cryptolab.symmetric.aes import aes_encrypt, aes_decrypt, aes_auto_analyze, AesResult
from cryptolab.symmetric.rc2 import rc2_encrypt, rc2_decrypt, rc2_auto_analyze, Rc2Result
from cryptolab.hashing import (
    hash_compute,
    hash_file,
    hmac_compute,
    hmac_verify,
    pbkdf2_hash,
    pbkdf2_verify,
    bcrypt_hash,
    bcrypt_verify,
    hash_verify_integrity,
    generate_random_bytes,
    HashResult,
    HMACResult,
    PasswordHashResult,
    VerifyPasswordResult,
    BCRYPT_AVAILABLE,
)
from cryptolab.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
    RSAKeyPair,
    RSAResult,
    DHKeyExchangeResult,
)
from cryptolab.analysis.auto_engine import run_auto_analysis, AutoAnalysisReport, AutoCandidate
from cryptolab.analysis.brute_force import caesar_brute_force, find_best_candidate, CaesarCandidate
from cryptolab.utils.history import log_history, read_history, clear_history, get_history_file

DIVIDER = "-" * 56
THIN_DIVIDER = "." * 56
HINTS_MAIN = [("↑↓", "navigasi"), ("enter", "pilih"), ("q", "keluar"), ("?", "bantuan")]
HINTS_SUB = [("↑↓", "navigasi"), ("enter", "pilih"), ("esc", "kembali"), ("q", "keluar"), ("?", "bantuan")]
LOGO_LARGE = """\
 ██████ ██████  ██    ██ ██████  ████████  ██████  ██       █████  ██████
██      ██   ██  ██  ██  ██   ██    ██    ██    ██ ██      ██   ██ ██   ██
██      ██████    ████   ██████     ██    ██    ██ ██      ███████ ██████
██      ██   ██    ██    ██         ██    ██    ██ ██      ██   ██ ██   ██
 ██████ ██   ██    ██    ██         ██     ██████  ███████ ██   ██ ██████"""

_PIXEL_FONT = {
    "C": [".####", "#....", "#....", "#....", ".####"],
    "R": ["####.", "#...#", "####.", "#..#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#.."],
    "P": ["####.", "#...#", "####.", "#....", "#...."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    "O": [".###.", "#...#", "#...#", "#...#", ".###."],
    "L": ["#....", "#....", "#....", "#....", "#####"],
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "B": ["####.", "#...#", "####.", "#...#", "####."],
}


def _build_pixel_logo(word: str) -> str:
    rows = ["" for _ in range(5)]
    for index, character in enumerate(word):
        for row in range(5):
            rows[row] += _PIXEL_FONT[character][row] + ("." if index < len(word) - 1 else "")
    rows.append("." * len(rows[0]))
    output = []
    for row in range(0, 6, 2):
        line = ""
        for top, bottom in zip(rows[row], rows[row + 1]):
            line += "█" if top == "#" and bottom == "#" else "▀" if top == "#" else "▄" if bottom == "#" else " "
        output.append(line.rstrip())
    return "\n".join(output)


LOGO_MEDIUM = _build_pixel_logo("CRYPTOLAB")
LOGO_TINY = "[ CRYPTOLAB ]"
LOGO = LOGO_MEDIUM

HELP_CATEGORIES = {
    "Navigasi CLI": [
        "↑ / ↓: pindah pilihan; Enter: pilih menu.",
        "Home / End: lompat ke pilihan pertama/terakhir.",
        "?: buka bantuan; Q: keluar; B atau Esc: kembali.",
        "Input data seperti key, IV, plaintext, dan ciphertext tetap diketik sebagai teks.",
    ],
    "Classical Cipher": [
        "Caesar: substitusi alfabet dengan nilai shift; tersedia encrypt, decrypt, brute force.",
        "Vigenere: substitusi polialfabetik berbasis keyword alfabet.",
        "Rail Fence: transposisi teks berbasis jumlah rail untuk latihan cipher klasik.",
        "Playfair: substitusi pasangan huruf menggunakan matriks keyword 5x5.",
        "Hill: cipher matriks yang memerlukan key matrix invertible.",
    ],
    "Symmetric Cipher": [
        "DES: block cipher legacy 64-bit; CBC/ECB dan PKCS#7/None.",
        "AES: block cipher modern; CBC/ECB, key 128/192/256-bit, PKCS#7/None.",
        "RC2/ARC2: block cipher legacy 64-bit; CBC/ECB, key 5-16 byte.",
        "CBC membutuhkan IV; ECB tidak menggunakan IV. Jangan gunakan cipher legacy untuk sistem baru.",
    ],
    "Hashing & Password": [
        "MD5/SHA-1: tersedia untuk kompatibilitas/latihan, bukan password atau keamanan modern.",
        "SHA-256/SHA-512: hash satu arah untuk integritas data.",
        "HMAC: autentikasi pesan dengan secret key dan hash.",
        "PBKDF2: derivasi key/password dengan salt, iterations, algorithm, dan dklen.",
        "Bcrypt: password hashing adaptif dengan cost/rounds; verifikasi memakai hash tersimpan.",
    ],
    "RSA & Diffie-Hellman": [
        "RSA: generate keypair, encrypt/decrypt, sign/verify.",
        "RSA encryption: OAEP direkomendasikan; PKCS#1 v1.5 hanya untuk kompatibilitas legacy.",
        "RSA signature: PSS direkomendasikan; PKCS#1 v1.5 untuk kompatibilitas.",
        "Diffie-Hellman: simulasi pertukaran secret dan derivasi key bersama.",
    ],
    "Encoding": [
        "Base64: representasi binary ke teks, bukan enkripsi dan tidak memakai key.",
        "Hex: representasi byte heksadesimal dengan delimiter opsional.",
        "Binary: representasi byte 8-bit dengan delimiter opsional.",
    ],
    "Analysis & History": [
        "Auto Analyze: deteksi encoding, pipeline decoding, Caesar brute force, dan cipher berkunci.",
        "Format detection: indikator heuristik untuk Hex, Base64, dan Binary.",
        "History: menyimpan ringkasan operasi lokal tanpa key/IV secara default.",
        "Skor readability adalah heuristik; selalu verifikasi hasil dengan konteks challenge.",
    ],
}


def terminal_width(default: int = 80) -> int:
    """Return the current terminal width for responsive rendering."""
    return shutil.get_terminal_size((default, 24)).columns


def _block_width(text: str) -> int:
    return max((len(line) for line in text.splitlines()), default=0)


def pick_logo(width: int) -> str:
    for logo in (LOGO_LARGE, LOGO_MEDIUM):
        if _block_width(logo) <= width:
            return logo
    return LOGO_TINY


def center_block(text: str, width: int, offset: int = 0) -> str:
    padding = max((width - _block_width(text)) // 2 + offset, 0)
    return "\n".join(" " * padding + line for line in text.splitlines())


class BackToMenu(Exception):
    """Raised when user chooses to navigate back to the previous menu."""
    pass


class ExitApp(Exception):
    """Raised when user chooses to exit the application."""
    pass


def _supports_color() -> bool:
    """Check if console output supports ANSI color codes safely."""
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        return os.environ.get("WT_SESSION") is not None or "ANSICON" in os.environ or os.environ.get("TERM") is not None
    return True


USE_COLOR = _supports_color()


def color_text(text: str, code: str) -> str:
    """Apply ANSI styling if terminal supports it, else return plain text."""
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return color_text(text, "1")


def cyan(text: str) -> str:
    return color_text(text, "36")


def green(text: str) -> str:
    return color_text(text, "32")


def yellow(text: str) -> str:
    return color_text(text, "33")


def red(text: str) -> str:
    return color_text(text, "31")


def emphasis(text: str) -> str:
    return color_text(text, "1;97")


def muted(text: str) -> str:
    return color_text(text, "90")


def _fit_hints(hints: List[Tuple[str, str]], width: int, gap: int = 3) -> List[Tuple[str, str]]:
    """Keep the highest-priority footer hints that fit the terminal."""
    chosen = list(hints)
    while chosen:
        plain = (" " * gap).join(f"{key} {label}" for key, label in chosen)
        if len(plain) <= max(width, 20):
            return chosen
        chosen.pop()
    return []


def render_footer(hints: List[Tuple[str, str]], width: Optional[int] = None, gap: int = 3) -> str:
    """Render compact keyboard hints with emphasized keys and muted labels."""
    width = width or terminal_width()
    gap = 1 if width < 40 else gap
    chosen = _fit_hints(hints, width, gap)
    plain = (" " * gap).join(f"{key} {label}" for key, label in chosen)
    styled = (" " * gap).join(
        f"{emphasis(key)} {muted(label)}" for key, label in chosen
    )
    padding = max((width - len(plain)) // 2, 0)
    divider = "-" * max(20, width - 2)
    return f"{center_block(divider, width)}\n{' ' * padding}{styled}"


def safe_input(prompt: str, allow_back: bool = True) -> str:
    """Read line from user safely, handling back navigation and interruptions."""
    try:
        user_val = input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()
        raise BackToMenu()

    cleaned = user_val.strip()
    if allow_back and cleaned.lower() in ("b", "kembali", "back"):
        raise BackToMenu()

    return cleaned


def render_card(
    title: str,
    method: str,
    operation: str,
    status: str,
    input_text: str,
    output_text: str,
    reasons: Optional[List[str]] = None,
    extra_fields: Optional[Dict[str, str]] = None,
) -> str:
    """Render a compact result panel for the interactive terminal."""
    status_lower = status.lower()
    if any(token in status_lower for token in ("gagal", "error", "kesalahan")):
        styled_status = red(status)
    elif any(token in status_lower for token in ("berhasil", "ok", "valid")):
        styled_status = green(status)
    else:
        styled_status = yellow(status)

    lines = [
        "",
        f"  {title.upper()}",
        f"  {method}  |  {operation}",
        f"  Status: {styled_status}",
    ]

    if extra_fields:
        for k, v in extra_fields.items():
            lines.append(f"  {k}: {v}")

    lines.extend([
        "",
        "  Input",
        f"  {input_text}",
        "",
        "  Output",
        f"  {output_text}",
    ])

    if reasons:
        lines.append("")
        lines.append(f"  Catatan: {'; '.join(reasons)}")

    lines.append("")
    return "\n".join(lines)


def save_result_prompt(content: str, default_filename: str = "hasil_cryptolab.txt") -> None:
    """Prompt user to optionally save text content to a file."""
    try:
        choice = safe_input(f"\n  Simpan hasil ke file? (y/n) [n]: ", allow_back=False).lower()
        if choice in ("y", "ya", "yes"):
            fn_input = safe_input(f"  Nama file [{default_filename}]: ", allow_back=False)
            filename = fn_input or default_filename
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")
            print(green(f"  [OK] Hasil berhasil disimpan ke: {filepath.resolve()}"))
    except Exception as err:
        print(red(f"  [!] Gagal menyimpan file: {err}"))


def post_result_menu(
    result_text: str, default_filename: str = "hasil_cryptolab.txt"
) -> bool:
    """Display post-result options. Returns True if user wants to repeat, False to go back."""
    while True:
        choice = navigation_menu(
            options=[
                "Ulangi proses / Coba data lain",
                "Simpan hasil ke file",
                "Kembali ke menu utama",
            ],
            title="OPSI SETELAH PROSES",
            back_label="Kembali ke menu utama",
            clear_display=False,
        )
        if choice is None or choice == 2:
            return False
        elif choice == 0:
            return True
        elif choice == 1:
            save_result_prompt(result_text, default_filename)


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
    
    def clear_screen():
        """Clear the terminal screen."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    
    def render_menu_initial():
        """Initial full render of the menu."""
        nonlocal menu_rendered
        width = terminal_width()
        if clear_display:
            clear_screen()
        elif menu_rendered:
            # Restore the menu origin and remove only the previous menu.
            sys.stdout.write("\033[u\033[J")
        else:
            # Keep the result card visible above this menu.
            sys.stdout.write("\033[s")
        if banner:
            banner_text = pick_logo(width) if banner_responsive else banner
            print(center_block(banner_text.rstrip("\n"), width, offset=-4))
        print(center_block(title[:max(20, width - 2)], width, offset=-4))
        print()
        sys.stdout.write("\033[s")
        for i, opt in enumerate(options):
            option_text = opt if len(opt) <= width - 8 else opt[:max(1, width - 11)] + "..."
            if i == selected:
                print(emphasis(f"  ▸ {option_text}"))
            else:
                print(muted(f"    {option_text}"))
        print(render_footer(HINTS_SUB if allow_back else HINTS_MAIN, width))
        print()
        sys.stdout.flush()
        menu_rendered = True
    
    def update_selection(old_idx: int, new_idx: int):
        """Update only the selection indicators without full redraw."""
        width = terminal_width()
        sys.stdout.write("\033[u")
        for i, opt in enumerate(options):
            option_text = opt if len(opt) <= width - 8 else opt[:max(1, width - 11)] + "..."
            prefix = "  ▸ " if i == selected else "    "
            styled = emphasis(prefix + option_text) if i == selected else muted(prefix + option_text)
            sys.stdout.write(f"\033[2K\r{styled}\n")
        sys.stdout.flush()

    def show_help():
        """Show categorized algorithm help without adding help to the options."""
        category_names = list(HELP_CATEGORIES)
        while True:
            category = navigation_menu(
                category_names,
                title="BANTUAN CRYPTOLAB - PILIH KATEGORI",
                allow_back=True,
                back_label="Kembali ke menu",
                clear_display=clear_display,
                help_enabled=False,
            )
            if category is None:
                render_menu_initial()
                return

            if clear_display:
                clear_screen()
            print("\n  " + category_names[category].upper())
            print()
            for item in HELP_CATEGORIES[category_names[category]]:
                print("  - " + item)
            print("\n  Tekan tombol apa saja untuk kembali ke kategori.")
            key = readchar.readkey()
            if key.lower() in ("q", "b") or key == getattr(readchar_key, "ESC", "\x1b"):
                render_menu_initial()
                return
    
    # Initial render
    render_menu_initial()
    
    while True:
        try:
            k = readchar.readkey()
        except (KeyboardInterrupt, EOFError):
            return None
        
        home_key = getattr(readchar_key, "HOME", "\x1b[H")
        end_key = getattr(readchar_key, "END", "\x1b[F")
        if k == readchar_key.UP:
            if selected > 0:
                old = selected
                selected -= 1
                update_selection(old, selected)
        elif k == readchar_key.DOWN:
            if selected < options_count - 1:
                old = selected
                selected += 1
                update_selection(old, selected)
        elif k == home_key:
            if selected != 0:
                old = selected
                selected = 0
                update_selection(old, selected)
        elif k == end_key:
            if selected != options_count - 1:
                old = selected
                selected = options_count - 1
                update_selection(old, selected)
        elif k in (readchar_key.ENTER, '\r', '\n'):
            if clear_display:
                clear_screen()
            return selected
        elif k.lower() in ('q',):
            if clear_display:
                clear_screen()
            return None
        elif help_enabled and k == '?':
            show_help()
        elif allow_back and (k.lower() in ('b', '0') or k == getattr(readchar_key, "ESC", "\x1b")):
            if clear_display:
                clear_screen()
            return None
        # Ignore other keys


# ======================================================================
# HANDLERS UNTUK SETIAP MENU
# ======================================================================

def handle_auto_analyze() -> None:
    """Interactive handler for Auto Analyze feature."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - AUTO ANALYZE (DETEKSI & ANALISIS CERDAS)")
        print(DIVIDER)
        print("  Fitur ini otomatis mendeteksi encoding (Base64, Hex, Binary),")
        print("  menguji decoding bertingkat, dan mencoba Caesar brute-force.")
        print("  Ketik 'b' untuk kembali ke menu utama kapan saja.")
        print(THIN_DIVIDER)

        try:
            ciphertext = safe_input("  Masukkan ciphertext atau data yang ingin dianalisis: ")
            if not ciphertext:
                print(yellow("  [!] Input tidak boleh kosong."))
                continue

            print("\n  [*] Menganalisis format encoding (Base64, Hex, Binary)...")
            print("  [*] Menguji pipeline decoding bertingkat...")
            print("  [*] Menguji Caesar brute-force (26 kemungkinan shift)...")

            # First run keyless analysis
            report: AutoAnalysisReport = run_auto_analysis(ciphertext)

            user_key: Optional[str] = None
            user_iv: Optional[str] = None

            # Check if keyed cipher is possible or confidence is low
            if report.possible_keyed_ciphers or not report.has_high_confidence:
                print(THIN_DIVIDER)
                if report.possible_keyed_ciphers:
                    keyed_list = ", ".join(report.possible_keyed_ciphers)
                    print(yellow(f"  [Indikator] Karakteristik data cocok dengan cipher ber-kunci ({keyed_list})."))

                key_input = safe_input(
                    "  Metode ini mungkin membutuhkan key. Masukkan key jika tersedia, atau tekan Enter untuk melewati: "
                )
                if key_input:
                    user_key = key_input
                    key_bytes_len = len(user_key.encode("utf-8"))

                    # AES uses a 16-byte key; DES and RC2 use an 8-byte key.
                    if key_bytes_len == 16 and (
                        "AES" in report.possible_keyed_ciphers or not report.possible_keyed_ciphers
                    ):
                        if key_bytes_len != 16:
                            print(yellow(f"  [Perhatian] Panjang key AES-128 harus tepat 16 byte (saat ini: {key_bytes_len} byte)."))
                        else:
                            iv_input = safe_input(
                                "  Metode AES CBC membutuhkan IV (16 byte). Masukkan IV jika ada, atau tekan Enter untuk mode ECB: "
                            )
                            if iv_input:
                                iv_bytes_len = len(iv_input.encode("utf-8"))
                                if iv_bytes_len != 16:
                                    print(yellow(f"  [Perhatian] Panjang IV AES CBC harus tepat 16 byte. Melewati CBC ber-IV."))
                                else:
                                    user_iv = iv_input

                    elif key_bytes_len == 8 and (
                        "DES" in report.possible_keyed_ciphers or "RC2" in report.possible_keyed_ciphers
                    ):
                        if key_bytes_len != 8:
                            print(yellow(f"  [Perhatian] Panjang key DES harus tepat 8 byte (saat ini: {key_bytes_len} byte)."))
                        else:
                            iv_input = safe_input(
                                "  Metode DES/RC2 CBC membutuhkan IV (8 byte). Masukkan IV jika ada, atau tekan Enter untuk mode ECB saja: "
                            )
                            if iv_input:
                                iv_bytes_len = len(iv_input.encode("utf-8"))
                                if iv_bytes_len != 8:
                                    print(yellow(f"  [Perhatian] Panjang IV DES CBC harus tepat 8 byte. Melewati CBC ber-IV."))
                                else:
                                    user_iv = iv_input

                    elif "AES" in report.possible_keyed_ciphers:
                        print(yellow(f"  [Perhatian] Panjang key AES-128 harus tepat 16 byte (saat ini: {key_bytes_len})."))

                    # Re-run analysis with supplied parameters
                    report = run_auto_analysis(ciphertext, key=user_key, iv=user_iv)

            # Display results
            top = report.top_candidate
            if top:
                card = render_card(
                    title="HASIL ANALISIS CRYPTOLAB",
                    method=top.method,
                    operation=top.operation,
                    status=top.status,
                    input_text=ciphertext,
                    output_text=top.output_text,
                    reasons=top.reasons,
                    extra_fields={
                        "Kategori": top.category,
                        "Skor Teks": f"{top.score:.1f}/100 ({top.score_level})",
                    },
                )
                print("\n" + card)

                # Show alternative candidates if available
                alt_candidates = [c for c in report.candidates if c != top][:4]
                if alt_candidates:
                    print("\n  KANDIDAT ALTERNATIF LAIN:")
                    print("  ------------------------------------------------------------------")
                    for idx, alt in enumerate(alt_candidates, start=1):
                        flag_mark = " [FLAG!]" if alt.flag_detected else ""
                        prev = alt.output_text[:40] + ("..." if len(alt.output_text) > 40 else "")
                        print(f"  [{idx}] {alt.method} ({alt.category}) | Skor: {alt.score:.1f}/100{flag_mark}")
                        print(f"      Hasil: {prev}")

                print(THIN_DIVIDER)
                print(f"  Catatan: {report.notes}")
                print("  Perhatian: Base64/Hex/Binary adalah encoding, bukan enkripsi ber-kunci.")
                print("  Hasil heuristik adalah estimasi terbaik dan perlu diverifikasi dengan konteks.")
                print(DIVIDER)

                log_history(
                    "Auto Analyze",
                    ciphertext,
                    top.output_text,
                    {"method": top.method, "score": top.score},
                )

                repeat = post_result_menu(card, "hasil_auto_analyze.txt")
                if not repeat:
                    break
            else:
                print(yellow("\n  [!] Tidak ditemukan kandidat yang menghasilkan teks terbaca."))
                print(yellow("      Ciphertext mungkin menggunakan key yang belum dimasukkan."))
                repeat = post_result_menu("Tidak ada kandidat.", "hasil_auto_analyze.txt")
                if not repeat:
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_caesar() -> None:
    """Interactive handler for Caesar Cipher."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - CAESAR CIPHER")
        print(DIVIDER)
        choice = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext dengan Shift Diketahui)",
                "Brute Force (Uji Seluruh 26 Pergeseran / Cari Shift Otomatis)",
            ],
            title="CRYPTOLAB - CAESAR CIPHER",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice in (0, 1):
                op_name = "Enkripsi" if choice == 0 else "Dekripsi"
                text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
                if not text:
                    print(yellow("  [!] Teks tidak boleh kosong."))
                    continue

                shift_str = safe_input("  Masukkan nilai shift (bilangan bulat): ")
                try:
                    shift = int(shift_str)
                except ValueError:
                    print(red("  [!] Shift harus berupa angka bulat (contoh: 3 atau -5)."))
                    continue

                if choice == 0:
                    out = caesar_encrypt(text, shift)
                    card = render_card(
                        title="HASIL OPERASI CRYPTOLAB",
                        method="Caesar Cipher",
                        operation="Enkripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=out,
                        extra_fields={"Shift": str(shift)},
                    )
                    log_history("Caesar Encrypt", text, out, {"shift": shift})
                else:
                    out = caesar_decrypt(text, shift)
                    card = render_card(
                        title="HASIL OPERASI CRYPTOLAB",
                        method="Caesar Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=out,
                        extra_fields={"Shift": str(shift)},
                    )
                    log_history("Caesar Decrypt", text, out, {"shift": shift})

                print("\n" + card)
                if not post_result_menu(card, "hasil_caesar.txt"):
                    break

            elif choice == 2:
                text = safe_input("  Masukkan ciphertext Caesar: ")
                if not text:
                    print(yellow("  [!] Ciphertext tidak boleh kosong."))
                    continue

                candidates = caesar_brute_force(text)
                best = find_best_candidate(candidates)

                view_opt = safe_input("  Tampilkan hanya kandidat terbaik? (y/n) [n]: ").lower()

                if view_opt in ("y", "ya", "yes") and best:
                    card = render_card(
                        title="HASIL ANALISIS CAESAR BRUTE FORCE",
                        method=f"Caesar Cipher (Shift {best.shift:02d})",
                        operation="Brute Force (Kandidat Terbaik)",
                        status="Kandidat ditemukan",
                        input_text=text,
                        output_text=best.text,
                        reasons=best.reasons,
                        extra_fields={
                            "Shift": f"{best.shift:02d}",
                            "Skor Teks": f"{best.score:.1f}/100 ({best.score_level})",
                        },
                    )
                    print("\n" + card)
                    log_history("Caesar Brute Force", text, best.text, {"best_shift": best.shift})
                    if not post_result_menu(card, "hasil_caesar_bruteforce.txt"):
                        break
                else:
                    print("\n" + DIVIDER)
                    print("  TABEL 26 KANDIDAT CAESAR BRUTE FORCE")
                    print(DIVIDER)
                    print("  Shift | Skor Huruf | Flag | Teks Hasil Dekripsi")
                    print("  ------+------------+------+----------------------------------------")
                    for c in candidates:
                        is_best = best and c.shift == best.shift
                        tag = "  <-- (Kemungkinan Terbesar)" if is_best else ""
                        flag_m = "FLAG" if c.flag_detected else "    "
                        print(f"   [{c.shift:02d}]  |   {c.common_ratio*100:5.1f}%   | {flag_m} | {c.text}{tag}")
                    print(DIVIDER)
                    if best:
                        print(green(f"  Kandidat Terbaik: Shift {best.shift:02d} -> {best.text}"))
                        log_history("Caesar Brute Force", text, best.text, {"best_shift": best.shift})
                    if not post_result_menu(best.text if best else "", "hasil_caesar_bruteforce.txt"):
                        break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_vigenere() -> None:
    """Interactive handler for Vigenere Cipher."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - VIGENERE CIPHER")
        print(DIVIDER)
        choice = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext)",
            ],
            title="CRYPTOLAB - VIGENERE CIPHER",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            op_name = "Enkripsi" if choice == 0 else "Dekripsi"
            text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
            if not text:
                print(yellow("  [!] Teks tidak boleh kosong."))
                continue

            key = safe_input("  Masukkan kata kunci (huruf alfabet A-Z): ")
            if not key:
                print(yellow("  [!] Kunci tidak boleh kosong."))
                continue
            if not all(c.isalpha() for c in key):
                print(red("  [!] Kunci hanya boleh berisi huruf alfabet tanpa angka atau simbol."))
                continue

            if choice == 0:
                out = vigenere_encrypt(text, key)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Vigenere Cipher",
                    operation="Enkripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=out,
                    extra_fields={"Panjang Kunci": str(len(key))},
                )
                # Do NOT log secret key to history
                log_history("Vigenere Encrypt", text, out, {"key_length": len(key)})
            else:
                out = vigenere_decrypt(text, key)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Vigenere Cipher",
                    operation="Dekripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=out,
                    extra_fields={"Panjang Kunci": str(len(key))},
                )
                # Do NOT log secret key to history
                log_history("Vigenere Decrypt", text, out, {"key_length": len(key)})

            print("\n" + card)
            if not post_result_menu(card, "hasil_vigenere.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_playfair() -> None:
    """Interactive handler for Playfair Cipher."""
    while True:
        sel = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext)",
            ],
            title="CRYPTOLAB - PLAYFAIR CIPHER (5x5 Matrix)",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
            if not text:
                print(yellow("  [!] Teks tidak boleh kosong."))
                continue

            key = safe_input("  Masukkan kata kunci (huruf alfabet A-Z): ")
            if not key:
                print(yellow("  [!] Kunci tidak boleh kosong."))
                continue
            if not all(c.isalpha() for c in key):
                print(red("  [!] Kunci hanya boleh berisi huruf alfabet tanpa angka atau simbol."))
                continue

            if sel == 0:
                res = playfair_encrypt(text, key)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Playfair Cipher",
                    operation="Enkripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=res.output_text,
                    extra_fields={"Key": key, "Matrix": "5x5 (I=J)"},
                )
                log_history("Playfair Encrypt", text, res.output_text, {"key": key})
            else:
                res = playfair_decrypt(text, key)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Playfair Cipher",
                    operation="Dekripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=res.output_text,
                    extra_fields={"Key": key, "Note": "Mungkin mengandung padding X"},
                )
                log_history("Playfair Decrypt", text, res.output_text, {"key": key})

            print("\n" + card)
            if not post_result_menu(card, "hasil_playfair.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_hill() -> None:
    """Interactive handler for Hill Cipher."""
    while True:
        sel = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext)",
            ],
            title="CRYPTOLAB - HILL CIPHER (Matrix 2x2 / 3x3)",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            size_sel = navigation_menu(
                options=["2x2 Matrix", "3x3 Matrix"],
                title="HILL CIPHER - Pilih Ukuran Matrix",
                back_label="Kembali",
            )
            if size_sel is None:
                continue
            size = 2 if size_sel == 0 else 3

            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
            if not text:
                print(yellow("  [!] Teks tidak boleh kosong."))
                continue

            key = safe_input(f"  Masukkan key matrix {size}x{size} (angka 0-25, spasi pemisah): ")
            if not key:
                print(yellow("  [!] Key matrix tidak boleh kosong."))
                continue

            try:
                if sel == 0:
                    res = hill_encrypt(text, key, size)
                    card = render_card(
                        title=f"HASIL OPERASI CRYPTOLAB - HILL {size}x{size}",
                        method="Hill Cipher",
                        operation="Enkripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Key Matrix": key, "Size": f"{size}x{size}", "Det": res.determinant, "DetInv": res.determinant_inv},
                    )
                    log_history(f"Hill {size}x{size} Encrypt", text, res.output_text, {"key": key, "size": size})
                else:
                    res = hill_decrypt(text, key, size)
                    card = render_card(
                        title=f"HASIL OPERASI CRYPTOLAB - HILL {size}x{size}",
                        method="Hill Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Key Matrix": key, "Size": f"{size}x{size}", "Note": "Mungkin mengandung padding X"},
                    )
                    log_history(f"Hill {size}x{size} Decrypt", text, res.output_text, {"key": key, "size": size})

                print("\n" + card)
                if not post_result_menu(card, f"hasil_hill_{size}x{size}.txt"):
                    break

            except CryptoLabError as err:
                print(red(f"\n  [!] Kesalahan Hill: {err}"))
            except Exception as err:
                print(red(f"\n  [!] Kesalahan tak terduga: {err}"))

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_affine() -> None:
    """Interactive handler for Affine Cipher."""
    while True:
        sel = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext)",
                "Brute Force (Cari kunci a,b)",
            ],
            title="CRYPTOLAB - AFFINE CIPHER E(x) = (ax + b) mod 26",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            if sel == 2:
                # Brute force
                text = safe_input("  Masukkan ciphertext: ")
                if not text:
                    print(yellow("  [!] Ciphertext tidak boleh kosong."))
                    continue
                
                candidates = affine_brute_force(text)
                if not candidates:
                    print(yellow("  [!] Tidak ada kandidat valid."))
                    continue
                
                best = candidates[0]
                card = render_card(
                    title="HASIL AFFINE BRUTE FORCE",
                    method=f"Affine (Best: a={best.a}, b={best.b})",
                    operation="Brute Force",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=best.output_text,
                    extra_fields={"Total Candidates": len(candidates), "Top a": best.a, "Top b": best.b},
                )
                print("\n" + card)
                log_history("Affine Brute Force", text, best.output_text, {"candidates": len(candidates)})
                if not post_result_menu(card, "hasil_affine_brute.txt"):
                    break
                continue

            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
            if not text:
                print(yellow("  [!] Teks tidak boleh kosong."))
                continue

            a_str = safe_input("  Masukkan a (coprime dengan 26: 1,3,5,7,9,11,15,17,19,21,23,25): ")
            try:
                a = int(a_str)
            except ValueError:
                print(red("  [!] a harus angka integer."))
                continue

            b_str = safe_input("  Masukkan b (0-25): ")
            try:
                b = int(b_str)
            except ValueError:
                print(red("  [!] b harus angka integer."))
                continue

            try:
                if sel == 0:
                    res = affine_encrypt(text, a, b)
                    card = render_card(
                        title="HASIL OPERASI CRYPTOLAB - AFFINE",
                        method="Affine Cipher",
                        operation="Enkripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"a": str(a), "b": str(b), "a_inv": str(res.a_inv), "Valid a": f"{len(VALID_A_VALUES)} values"},
                    )
                    log_history("Affine Encrypt", text, res.output_text, {"a": a, "b": b})
                else:
                    res = affine_decrypt(text, a, b)
                    card = render_card(
                        title="HASIL OPERASI CRYPTOLAB - AFFINE",
                        method="Affine Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"a": str(a), "b": str(b), "a_inv": str(res.a_inv)},
                    )
                    log_history("Affine Decrypt", text, res.output_text, {"a": a, "b": b})

                print("\n" + card)
                if not post_result_menu(card, "hasil_affine.txt"):
                    break

            except CryptoLabError as err:
                print(red(f"\n  [!] Kesalahan: {err}"))
            except Exception as err:
                print(red(f"\n  [!] Kesalahan tak terduga: {err}"))

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_railfence() -> None:
    """Interactive handler for Rail Fence Cipher."""
    while True:
        sel = navigation_menu(
            options=[
                "Enkripsi (Plaintext -> Ciphertext)",
                "Dekripsi (Ciphertext -> Plaintext)",
                "Brute Force (Coba semua rail)",
            ],
            title="CRYPTOLAB - RAIL FENCE / TRANSPOSITION CIPHER",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            if sel == 2:
                # Brute force
                text = safe_input("  Masukkan ciphertext: ")
                if not text:
                    print(yellow("  [!] Ciphertext tidak boleh kosong."))
                    continue
                
                max_rails_str = safe_input("  Maksimal rail [10]: ")
                try:
                    max_rails = int(max_rails_str) if max_rails_str else 10
                except ValueError:
                    max_rails = 10
                
                candidates = railfence_brute_force(text, max_rails)
                if not candidates:
                    print(yellow("  [!] Tidak ada kandidat valid."))
                    continue
                
                best = candidates[0]
                card = render_card(
                    title="HASIL RAIL FENCE BRUTE FORCE",
                    method=f"Rail Fence (Best: {best.rails} rails)",
                    operation="Brute Force",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=best.output_text,
                    extra_fields={"Total Candidates": len(candidates), "Top Rails": best.rails},
                )
                print("\n" + card)
                log_history("Rail Fence Brute Force", text, best.output_text, {"candidates": len(candidates)})
                if not post_result_menu(card, "hasil_railfence_brute.txt"):
                    break
                continue

            rails_str = safe_input("  Jumlah rail (minimal 2): ")
            try:
                rails = int(rails_str)
                if rails < 2:
                    print(red("  [!] Minimal 2 rail."))
                    continue
            except ValueError:
                print(red("  [!] Rail harus angka integer."))
                continue

            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = safe_input(f"  Masukkan teks untuk {op_name.lower()}: ")
            if not text:
                print(yellow("  [!] Teks tidak boleh kosong."))
                continue

            try:
                if sel == 0:
                    res = railfence_encrypt(text, rails)
                    pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                    card = render_card(
                        title=f"HASIL OPERASI CRYPTOLAB - RAIL FENCE {rails} RAILS",
                        method="Rail Fence Cipher",
                        operation="Enkripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Rails": str(rails)},
                    )
                    print("\n" + card)
                    print(f"\n  Rail Pattern:\n{pattern_str}\n")
                    log_history(f"Rail Fence {rails} Encrypt", text, res.output_text, {"rails": rails})
                else:
                    res = railfence_decrypt(text, rails)
                    pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                    card = render_card(
                        title=f"HASIL OPERASI CRYPTOLAB - RAIL FENCE {rails} RAILS",
                        method="Rail Fence Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Rails": str(rails)},
                    )
                    print("\n" + card)
                    print(f"\n  Rail Pattern:\n{pattern_str}\n")
                    log_history(f"Rail Fence {rails} Decrypt", text, res.output_text, {"rails": rails})

                if not post_result_menu(card, f"hasil_railfence_{rails}.txt"):
                    break

            except CryptoLabError as err:
                print(red(f"\n  [!] Kesalahan: {err}"))
            except Exception as err:
                print(red(f"\n  [!] Kesalahan tak terduga: {err}"))

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_des() -> None:
    """Interactive handler for DES (CBC/ECB)."""
    while True:
        sel = navigation_menu(
            options=[
                "Dekripsi (Ciphertext Hex -> Plaintext)",
                "Enkripsi (Plaintext -> Ciphertext Hex)",
                "Auto Analisis Mode & Padding (Uji ECB & CBC)",
            ],
            title="CRYPTOLAB - DES (DATA ENCRYPTION STANDARD)",
            back_label="Kembali ke Menu Utama",
        )
        
        if sel is None:
            break
        
        try:
            if sel == 0:
                _handle_des_decrypt()
            elif sel == 1:
                _handle_des_encrypt()
            elif sel == 2:
                _handle_des_auto_analyze()
        
        except BackToMenu:
            continue
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan DES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_des_decrypt() -> None:
    """Handle DES decryption with mode selection."""
    while True:
        print("\n" + DIVIDER)
        print("  DES DEKRIPSI - Pilih Mode")
        print(DIVIDER)
        
        mode_sel = navigation_menu(
            options=[
                "Auto (analisis heuristik mode dan padding, key & IV opsional)",
                "CBC (Cipher Block Chaining - membutuhkan IV 8 byte)",
                "ECB (Electronic Codebook - tanpa IV)",
            ],
            title="DES DEKRIPSI - Pilih Mode",
            back_label="Kembali ke Menu DES",
        )
        
        if mode_sel is None:
            break
        
        try:
            ct_hex = safe_input("  Masukkan ciphertext (format heksadesimal): ")
            if not ct_hex:
                print(yellow("  [!] Ciphertext heksadesimal tidak boleh kosong."))
                continue

            if mode_sel == 0:
                # Auto mode - key and IV are optional
                print("\n  Mode Auto: Key dan IV opsional (tekan Enter untuk melewati)")
                key = safe_input("  Masukkan key (tepat 8 karakter/byte, Enter untuk skip): ")
                key_val = key if len(key.encode("utf-8")) == 8 else None
                
                iv = None
                if key_val:
                    iv_cand = safe_input("  Masukkan IV (8 karakter untuk CBC, Enter untuk skip/ECB): ")
                    iv = iv_cand if len(iv_cand.encode("utf-8")) == 8 else None
                
                if key_val is None:
                    print(yellow("  [!] Key dilewati. Auto analisis memerlukan key. Gunakan mode CBC/ECB manual."))
                    continue

                candidates: List[DesResult] = des_auto_analyze(ct_hex, key=key_val, iv=iv)

                if not candidates:
                    print(yellow("  [!] Tidak ada konfigurasi DES yang berhasil secara teknis."))
                    continue

                top = candidates[0]
                card = render_card(
                    title="HASIL ANALISIS DES (KANDIDAT TERBAIK)",
                    method=f"DES ({top.mode}, Padding {top.padding})",
                    operation="Dekripsi",
                    status="Kandidat ditemukan" if top.readable_success else "Dekripsi teknis berhasil (Plaintext belum terverifikasi)",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={
                        "Mode": top.mode,
                        "Padding": top.padding,
                        "Status UTF-8": "Valid" if top.is_utf8 else "Non-UTF8 (Tampil Hex)",
                    },
                )
                print("\n" + card)

                if len(candidates) > 1:
                    print("\n  KANDIDAT MODE/PADDING LAIN:")
                    print("  ------------------------------------------------------------------")
                    for idx, c in enumerate(candidates[1:], start=1):
                        prev = c.output_text[:35] + ("..." if len(c.output_text) > 35 else "")
                        print(f"  [{idx}] Mode {c.mode} | Padding {c.padding} | Skor: {c.score:.1f}/100 -> {prev}")

                print(THIN_DIVIDER)
                print("  Catatan: Ciphertext heksadesimal tidak membuktikan mode CBC atau ECB.")
                print("  Hasil ditampilkan sebagai kandidat heuristik terverifikasi.")
                print(DIVIDER)

                log_history("DES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                if not post_result_menu(card, "hasil_des.txt"):
                    break

            else:
                mode = "CBC" if mode_sel == 1 else "ECB"
                key = safe_input("  Masukkan key (tepat 8 karakter/byte): ")
                if len(key.encode("utf-8")) != 8:
                    print(red(f"  [!] Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
                    continue

                iv: Optional[str] = None
                if mode == "CBC":
                    iv = safe_input("  Masukkan IV (tepat 8 karakter/byte): ")
                    if len(iv.encode("utf-8")) != 8:
                        print(red(f"  [!] Panjang IV DES CBC harus tepat 8 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)."))
                        continue

                pad_sel = navigation_menu(
                    options=["PKCS#7 (standar default)", "Tanpa Padding (None)"],
                    title="DES DEKRIPSI - Pilih Padding",
                    back_label="Batal",
                )
                if pad_sel is None:
                    continue
                padding = "PKCS7" if pad_sel == 0 else "None"

                res = des_decrypt(ct_hex, key=key, mode=mode, iv=iv, padding=padding)

                status_msg = "Berhasil (Teks UTF-8 Terbaca)" if res.readable_success else "Berhasil Secara Teknis (Keterbacaan Rendah)"
                if not res.is_utf8:
                    status_msg = "Berhasil Secara Teknis (Bukan teks UTF-8 valid - Hasil berupa Hex)"

                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB - DES DECRYPT",
                    method=f"DES ({mode})",
                    operation="Dekripsi",
                    status=status_msg,
                    input_text=ct_hex,
                    output_text=res.output_text if res.is_utf8 else f"[Bytes Hex] {res.output_text}",
                    reasons=res.reasons,
                    extra_fields={
                        "Mode": mode,
                        "Padding": padding,
                        "Status UTF-8": "Valid" if res.is_utf8 else "Non-UTF8 (Tampil Hex)",
                    },
                )
                print("\n" + card)

                log_history("DES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                if not post_result_menu(card, "hasil_des.txt"):
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan DES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_des_encrypt() -> None:
    """Handle DES encryption."""
    while True:
        plaintext = safe_input("  Masukkan plaintext untuk dienkripsi: ")
        if not plaintext:
            print(yellow("  [!] Plaintext tidak boleh kosong."))
            continue

        mode_sel = navigation_menu(
            options=[
                "CBC (Cipher Block Chaining - membutuhkan IV 8 byte) [Default]",
                "ECB (Electronic Codebook - tanpa IV)",
            ],
            title="DES ENKRIPSI - Pilih Mode",
            back_label="Batal",
        )
        if mode_sel is None:
            break
        
        mode = "CBC" if mode_sel == 0 else "ECB"

        key = safe_input("  Masukkan key (tepat 8 karakter/byte): ")
        if len(key.encode("utf-8")) != 8:
            print(red(f"  [!] Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
            continue

        iv = None
        if mode == "CBC":
            iv = safe_input("  Masukkan IV (tepat 8 karakter/byte): ")
            if len(iv.encode("utf-8")) != 8:
                print(red(f"  [!] Panjang IV DES CBC harus tepat 8 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)."))
                continue

        pad_sel = navigation_menu(
            options=["PKCS#7 (standar default)", "Tanpa Padding (None - plaintext harus kelipatan 8 byte)"],
            title="DES ENKRIPSI - Pilih Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        padding = "PKCS7" if pad_sel == 0 else "None"

        res_enc = des_encrypt(plaintext, key=key, mode=mode, iv=iv, padding=padding)

        card = render_card(
            title="HASIL OPERASI CRYPTOLAB - DES ENCRYPT",
            method=f"DES ({mode})",
            operation="Enkripsi",
            status="Berhasil (OK)",
            input_text=plaintext,
            output_text=res_enc.output_text,
            reasons=["Enkripsi selesai tanpa kesalahan"],
            extra_fields={"Mode": mode, "Padding": padding},
        )
        print("\n" + card)

        log_history("DES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

        if not post_result_menu(card, "hasil_des_encrypt.txt"):
            break


def _handle_des_auto_analyze() -> None:
    """Handle DES auto analyze."""
    while True:
        print("\n" + DIVIDER)
        print("  DES AUTO ANALISIS")
        print(DIVIDER)
        print("  Fitur ini menguji kombinasi mode (CBC/ECB) dan padding (PKCS7/None)")
        print("  Key diperlukan, IV opsional (tekan Enter untuk melewati).")
        print(THIN_DIVIDER)

        try:
            ct_hex = safe_input("  Masukkan ciphertext heksadesimal: ")
            if not ct_hex:
                print(yellow("  [!] Ciphertext tidak boleh kosong."))
                continue

            key = safe_input("  Masukkan key (tepat 8 karakter/byte, Enter untuk skip): ")
            key_val = key if len(key.encode("utf-8")) == 8 else None
            
            iv_val: Optional[str] = None
            if key_val:
                iv_cand = safe_input("  Masukkan IV (8 karakter untuk CBC, Enter untuk skip): ")
                iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 8 else None
            
            if key_val is None:
                print(yellow("  [!] Key dilewati. DES tidak dapat didekripsi tanpa key."))
                continue

            candidates = des_auto_analyze(ct_hex, key=key_val, iv=iv_val)

            if candidates:
                top = candidates[0]
                card = render_card(
                    title="HASIL ANALISIS DES",
                    method=f"DES ({top.mode}, Padding {top.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={"Mode": top.mode, "Padding": top.padding},
                )
                print("\n" + card)
                log_history("DES Auto Analyze", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})
                if not post_result_menu(card, "hasil_des_auto.txt"):
                    break
            else:
                print(yellow("  [!] Tidak ada kombinasi DES yang valid dengan parameter tersebut."))

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan DES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_rc2() -> None:
    """Interactive handler for legacy RC2/ARC2 (CBC/ECB)."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - RC2 (ARC2) LEGACY 64-BIT")
        print(DIVIDER)
        print("  RC2 hanya untuk praktikum, CTF, dan kompatibilitas data lama.")
        print("  Default effective key length: 128 bit.")
        print(THIN_DIVIDER)
        choice = navigation_menu(
            options=[
                "Dekripsi (Ciphertext Hex -> Plaintext)",
                "Enkripsi (Plaintext -> Ciphertext Hex)",
                "Auto Analisis Mode & Padding",
            ],
            title="CRYPTOLAB - RC2 (ARC2) LEGACY 64-BIT",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice == 0:
                text = safe_input("  Masukkan ciphertext heksadesimal: ")
            elif choice == 1:
                text = safe_input("  Masukkan plaintext: ")
            else:
                text = safe_input("  Masukkan ciphertext heksadesimal: ")
            if not text:
                print(yellow("  [!] Input tidak boleh kosong."))
                continue

            key = safe_input("  Masukkan key RC2 (5-16 byte): ")
            if not 5 <= len(key.encode("utf-8")) <= 16:
                print(red(f"  [!] Panjang key RC2 harus 5-16 byte. Ditemukan: {len(key.encode('utf-8'))} byte."))
                continue

            iv: Optional[str] = None
            if choice == 2:
                iv_input = safe_input("  Masukkan IV CBC (8 byte), atau Enter untuk ECB: ")
                if iv_input:
                    if len(iv_input.encode("utf-8")) != 8:
                        print(red("  [!] Panjang IV RC2 CBC harus tepat 8 byte."))
                        continue
                    iv = iv_input
                candidates = rc2_auto_analyze(text, key=key, iv=iv)
                if not candidates:
                    print(yellow("  [!] Tidak ada konfigurasi RC2 yang berhasil."))
                    continue
                result = candidates[0]
                card = render_card(
                    title="HASIL ANALISIS RC2",
                    method=f"RC2 ({result.mode}, Padding {result.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=result.output_text if result.is_utf8 else f"[Bytes Hex] {result.output_text}",
                    reasons=result.reasons,
                    extra_fields={"Mode": result.mode, "Padding": result.padding, "Effective Key Length": "128 bit"},
                )
                print("\n" + card)
                log_history("RC2 Auto Analyze", text, result.output_text, {"mode": result.mode, "padding": result.padding})
                if not post_result_menu(card, "hasil_rc2_auto.txt"):
                    break
                continue

            mode_sel = navigation_menu(
                options=[
                    "CBC (Cipher Block Chaining - membutuhkan IV 8 byte)",
                    "ECB (Electronic Codebook - tanpa IV)",
                ],
                title="RC2 - Pilih Mode",
                back_label="Batal",
            )
            if mode_sel is None:
                continue
            mode = "CBC" if mode_sel == 0 else "ECB"
            if mode == "CBC":
                iv = safe_input("  Masukkan IV (tepat 8 karakter/byte): ")
                if len(iv.encode("utf-8")) != 8:
                    print(red("  [!] Panjang IV RC2 CBC harus tepat 8 byte."))
                    continue

            pad_sel = navigation_menu(
                options=["PKCS#7 (standar default)", "Tanpa Padding (None)"],
                title="RC2 - Pilih Padding",
                back_label="Batal",
            )
            if pad_sel is None:
                continue
            padding = "PKCS7" if pad_sel == 0 else "None"
            if choice == 0:
                result = rc2_decrypt(text, key=key, mode=mode, iv=iv, padding=padding)
                title, operation, output = "HASIL OPERASI CRYPTOLAB - RC2 DECRYPT", "Dekripsi", result.output_text
                history_operation = "RC2 Decrypt"
            else:
                result = rc2_encrypt(text, key=key, mode=mode, iv=iv, padding=padding)
                title, operation, output = "HASIL OPERASI CRYPTOLAB - RC2 ENCRYPT", "Enkripsi", result.output_text
                history_operation = "RC2 Encrypt"
            card = render_card(
                title=title,
                method=f"RC2 ({mode})",
                operation=operation,
                status="Berhasil (OK)",
                input_text=text,
                output_text=output,
                reasons=result.reasons,
                extra_fields={"Mode": mode, "Padding": padding, "Effective Key Length": "128 bit"},
            )
            print("\n" + card)
            log_history(history_operation, text, output, {"mode": mode, "padding": padding})
            if not post_result_menu(card, "hasil_rc2.txt"):
                break
        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan RC2: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_hashing() -> None:
    """Interactive handler for Hashing (MD5, SHA1, SHA256, SHA512, HMAC, PBKDF2, Bcrypt, Random)."""
    while True:
        options = [
            "Hash Compute (MD5, SHA1, SHA256, SHA512)",
            "Hash File",
            "Verifikasi Integritas (Hash)",
            "HMAC Compute & Verify",
            "PBKDF2 Hash & Verify Password",
        ]
        if BCRYPT_AVAILABLE:
            options.append("Bcrypt Hash & Verify Password")
        options.append("Generate Random Bytes")

        sel = navigation_menu(
            options=options,
            title="CRYPTOLAB - HASHING & PASSWORD SECURITY",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            if sel == 0:
                _handle_hash_compute()
            elif sel == 1:
                _handle_hash_file()
            elif sel == 2:
                _handle_hash_verify()
            elif sel == 3:
                _handle_hmac()
            elif sel == 4:
                _handle_pbkdf2()
            elif sel == 5 and BCRYPT_AVAILABLE:
                _handle_bcrypt()
            elif sel == 5 and not BCRYPT_AVAILABLE:
                _handle_random_bytes()
            elif sel == 6:
                _handle_random_bytes()
        except BackToMenu:
            continue
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan Hashing: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_hash_compute() -> None:
    """Handle hash computation."""
    while True:
        algo_sel = navigation_menu(
            options=["MD5 (128-bit)", "SHA1 (160-bit)", "SHA256 (256-bit)", "SHA512 (512-bit)"],
            title="HASH COMPUTE - Pilih Algoritma",
            back_label="Kembali",
        )
        if algo_sel is None:
            break
        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        algo = algorithms[algo_sel]

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title=f"{algo} - Pilih Format Output",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        data = safe_input(f"  Masukkan data untuk {algo} hash: ")
        if not data:
            print(yellow("  [!] Data tidak boleh kosong."))
            continue

        res = hash_compute(data, algorithm=algo, encoding=encoding)
        card = render_card(
            title=f"HASIL HASH {algo}",
            method=f"{algo} Hash",
            operation="COMPUTE",
            status="Berhasil (OK)",
            input_text=data,
            output_text=res.output_hash,
            reasons=[f"Output dalam format {encoding.upper()}"],
            extra_fields={"Algorithm": algo, "Encoding": encoding.upper()},
        )
        print("\n" + card)
        log_history(f"Hash {algo} Compute", data, res.output_hash, {"algo": algo, "encoding": encoding})
        if not post_result_menu(card, f"hasil_hash_{algo.lower()}.txt"):
            break


def _handle_hash_file() -> None:
    """Handle file hashing."""
    while True:
        filepath = safe_input("  Masukkan path file: ")
        if not filepath:
            print(yellow("  [!] Path file tidak boleh kosong."))
            continue

        algo_sel = navigation_menu(
            options=["MD5 (128-bit)", "SHA1 (160-bit)", "SHA256 (256-bit)", "SHA512 (512-bit)"],
            title="HASH FILE - Pilih Algoritma",
            back_label="Kembali",
        )
        if algo_sel is None:
            break
        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        algo = algorithms[algo_sel]

        try:
            res = hash_file(filepath, algorithm=algo)
            card = render_card(
                title=f"HASIL HASH FILE {algo}",
                method=f"{algo} Hash",
                operation="FILE",
                status="Berhasil (OK)",
                input_text=filepath,
                output_text=res.output_hash,
                reasons=["File dibaca dalam chunk 8KB"],
                extra_fields={"Algorithm": algo, "File": filepath},
            )
            print("\n" + card)
            log_history(f"Hash {algo} File", filepath, res.output_hash, {"algo": algo, "filepath": filepath})
            if not post_result_menu(card, f"hasil_hash_file_{algo.lower()}.txt"):
                break
        except InvalidInputError as e:
            print(red(f"  [!] {e}"))
        except Exception as e:
            print(red(f"  [!] Gagal membaca file: {e}"))


def _handle_hash_verify() -> None:
    """Handle hash integrity verification."""
    while True:
        algo_sel = navigation_menu(
            options=["MD5 (128-bit)", "SHA1 (160-bit)", "SHA256 (256-bit)", "SHA512 (512-bit)"],
            title="VERIFIKASI INTEGRITAS - Pilih Algoritma",
            back_label="Kembali",
        )
        if algo_sel is None:
            break
        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        algo = algorithms[algo_sel]

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title=f"{algo} Verify - Pilih Format Hash",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        data = safe_input("  Masukkan data asli: ")
        if not data:
            print(yellow("  [!] Data tidak boleh kosong."))
            continue

        expected = safe_input("  Masukkan hash yang diharapkan: ")
        if not expected:
            print(yellow("  [!] Hash yang diharapkan tidak boleh kosong."))
            continue

        res = hash_verify_integrity(data, expected, algorithm=algo, encoding=encoding)
        status = "VALID (COCOK)" if res.match else "INVALID (TIDAK COCOK)"
        card = render_card(
            title=f"VERIFIKASI INTEGRITAS {algo}",
            method=f"{algo} Verify",
            operation="VERIFY",
            status=status,
            input_text=data,
            output_text="COCOK" if res.match else "TIDAK COCOK",
            reasons=res.reasons,
            extra_fields={"Algorithm": algo, "Expected": expected, "Status": "VALID" if res.match else "INVALID"},
        )
        print("\n" + card)
        log_history(f"Hash {algo} Verify", data, "COCOK" if res.match else "TIDAK COCOK", {"algo": algo, "match": res.match})
        if not post_result_menu(card, f"hasil_hash_verify_{algo.lower()}.txt"):
            break


def _handle_hmac() -> None:
    """Handle HMAC operations."""
    while True:
        sel = navigation_menu(
            options=["HMAC Compute", "HMAC Verify"],
            title="HMAC - Hash-based Message Authentication Code",
            back_label="Kembali",
        )
        if sel is None:
            break

        algo_sel = navigation_menu(
            options=["HMAC-MD5", "HMAC-SHA1", "HMAC-SHA256", "HMAC-SHA512"],
            title="HMAC - Pilih Algoritma",
            back_label="Kembali",
        )
        if algo_sel is None:
            continue
        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        algo = algorithms[algo_sel]

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title=f"HMAC-{algo} - Pilih Format Output",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        if sel == 0:
            # Compute
            message = safe_input("  Masukkan pesan: ")
            if not message:
                print(yellow("  [!] Pesan tidak boleh kosong."))
                continue
            key = safe_input("  Masukkan kunci rahasia: ")
            if not key:
                print(yellow("  [!] Kunci tidak boleh kosong."))
                continue

            res = hmac_compute(message, key, algorithm=algo, encoding=encoding)
            card = render_card(
                title=f"HASIL HMAC-{algo}",
                method=f"HMAC-{algo}",
                operation="COMPUTE",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_hmac,
                reasons=[f"Key length: {len(key)} bytes", f"Output: {encoding.upper()}"],
                extra_fields={"Algorithm": f"HMAC-{algo}", "Encoding": encoding.upper()},
            )
            print("\n" + card)
            log_history(f"HMAC-{algo} Compute", message, res.output_hmac, {"algo": algo, "encoding": encoding})
            if not post_result_menu(card, f"hasil_hmac_{algo.lower()}.txt"):
                break

        else:
            # Verify
            message = safe_input("  Masukkan pesan: ")
            if not message:
                print(yellow("  [!] Pesan tidak boleh kosong."))
                continue
            key = safe_input("  Masukkan kunci rahasia: ")
            if not key:
                print(yellow("  [!] Kunci tidak boleh kosong."))
                continue
            expected = safe_input("  Masukkan HMAC yang diharapkan: ")
            if not expected:
                print(yellow("  [!] HMAC yang diharapkan tidak boleh kosong."))
                continue

            match = hmac_verify(message, key, expected, algorithm=algo, encoding=encoding)
            status = "VALID (COCOK)" if match else "INVALID (TIDAK COCOK)"
            card = render_card(
                title=f"VERIFIKASI HMAC-{algo}",
                method=f"HMAC-{algo}",
                operation="VERIFY",
                status=status,
                input_text=message,
                output_text="COCOK" if match else "TIDAK COCOK",
                reasons=["Konstanta-time comparison"],
                extra_fields={"Algorithm": f"HMAC-{algo}", "Status": "VALID" if match else "INVALID"},
            )
            print("\n" + card)
            log_history(f"HMAC-{algo} Verify", message, "COCOK" if match else "TIDAK COCOK", {"algo": algo, "match": match})
            if not post_result_menu(card, f"hasil_hmac_verify_{algo.lower()}.txt"):
                break


def _handle_pbkdf2() -> None:
    """Handle PBKDF2 operations."""
    while True:
        sel = navigation_menu(
            options=["PBKDF2 Hash Password", "PBKDF2 Verify Password"],
            title="PBKDF2 - Password-Based Key Derivation Function 2",
            back_label="Kembali",
        )
        if sel is None:
            break

        algo_sel = navigation_menu(
            options=["PBKDF2-SHA256", "PBKDF2-SHA512"],
            title="PBKDF2 - Pilih Algoritma",
            back_label="Kembali",
        )
        if algo_sel is None:
            continue
        algorithms = ["SHA256", "SHA512"]
        algo = algorithms[algo_sel]

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title=f"PBKDF2-{algo} - Pilih Format Output",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        if sel == 0:
            # Hash
            password = safe_input("  Masukkan password: ")
            if not password:
                print(yellow("  [!] Password tidak boleh kosong."))
                continue

            salt_input = safe_input("  Masukkan salt (hex/base64, kosong untuk random): ")
            salt = salt_input if salt_input else None

            iter_input = safe_input("  Jumlah iterasi [100000]: ")
            try:
                iterations = int(iter_input) if iter_input else 100000
                if iterations < 1000:
                    print(red("  [!] Iterations minimal 1000."))
                    continue
            except ValueError:
                print(red("  [!] Iterations harus angka."))
                continue

            dklen_input = safe_input("  Derived key length (bytes) [32]: ")
            try:
                dklen = int(dklen_input) if dklen_input else 32
                if dklen < 1 or dklen > 128:
                    print(red("  [!] DKLen harus 1-128 bytes."))
                    continue
            except ValueError:
                print(red("  [!] DKLen harus angka."))
                continue

            res = pbkdf2_hash(password, salt=salt, iterations=iterations, algorithm=algo, dklen=dklen, encoding=encoding)
            output_text = f"Salt: {res.salt}\nHash: {res.hash_value}"
            card = render_card(
                title=f"HASIL PBKDF2-{algo}",
                method=f"PBKDF2-{algo}",
                operation="HASH",
                status="Berhasil (OK)",
                input_text="********",
                output_text=output_text,
                reasons=[f"Salt: {len(bytes.fromhex(res.salt)) if encoding=='hex' else len(base64.b64decode(res.salt))} bytes", f"DKLen: {dklen} bytes", f"Output: {encoding.upper()}"],
                extra_fields={"Algorithm": f"PBKDF2-{algo}", "Iterations": f"{iterations:,}", "DKLen": f"{dklen} bytes", "Encoding": encoding.upper()},
            )
            print("\n" + card)
            log_history(f"PBKDF2-{algo} Hash", "********", res.hash_value, {"algo": algo, "iterations": iterations, "salt": res.salt})
            if not post_result_menu(card, f"hasil_pbkdf2_{algo.lower()}.txt"):
                break

        else:
            # Verify
            password = safe_input("  Masukkan password: ")
            if not password:
                print(yellow("  [!] Password tidak boleh kosong."))
                continue

            salt = safe_input("  Masukkan salt (hex/base64): ")
            if not salt:
                print(yellow("  [!] Salt tidak boleh kosong."))
                continue

            expected = safe_input("  Masukkan hash yang diharapkan: ")
            if not expected:
                print(yellow("  [!] Hash yang diharapkan tidak boleh kosong."))
                continue

            iter_input = safe_input("  Jumlah iterasi [100000]: ")
            try:
                iterations = int(iter_input) if iter_input else 100000
            except ValueError:
                print(red("  [!] Iterations harus angka."))
                continue

            dklen_input = safe_input("  Derived key length (bytes) [32]: ")
            try:
                dklen = int(dklen_input) if dklen_input else 32
            except ValueError:
                print(red("  [!] DKLen harus angka."))
                continue

            res = pbkdf2_verify(password, salt, expected, iterations=iterations, algorithm=algo, dklen=dklen, encoding=encoding)
            status = "COCOK" if res.match else "TIDAK COCOK"
            card = render_card(
                title=f"VERIFIKASI PBKDF2-{algo}",
                method=f"PBKDF2-{algo}",
                operation="VERIFY",
                status=status,
                input_text="********",
                output_text=status,
                reasons=res.reasons,
                extra_fields={"Algorithm": f"PBKDF2-{algo}", "Status": status},
            )
            print("\n" + card)
            log_history(f"PBKDF2-{algo} Verify", "********", status, {"algo": algo, "match": res.match})
            if not post_result_menu(card, f"hasil_pbkdf2_verify_{algo.lower()}.txt"):
                break


def _handle_bcrypt() -> None:
    """Handle Bcrypt operations."""
    while True:
        sel = navigation_menu(
            options=["Bcrypt Hash Password", "Bcrypt Verify Password"],
            title="BCRYPT - Adaptive Password Hashing",
            back_label="Kembali",
        )
        if sel is None:
            break

        if sel == 0:
            # Hash
            password = safe_input("  Masukkan password: ")
            if not password:
                print(yellow("  [!] Password tidak boleh kosong."))
                continue

            rounds_input = safe_input("  Cost factor/rounds (4-31) [12]: ")
            try:
                rounds = int(rounds_input) if rounds_input else 12
                if rounds < 4 or rounds > 31:
                    print(red("  [!] Rounds harus 4-31."))
                    continue
            except ValueError:
                print(red("  [!] Rounds harus angka."))
                continue

            res = bcrypt_hash(password, rounds=rounds)
            card = render_card(
                title="HASIL BCRYPT",
                method="BCRYPT",
                operation="HASH",
                status="Berhasil (OK)",
                input_text="********",
                output_text=res.hash_value,
                reasons=["Adaptive hash dengan salt otomatis", "Cocok untuk penyimpanan password"],
                extra_fields={"Algorithm": "BCRYPT", "Rounds": str(rounds)},
            )
            print("\n" + card)
            log_history("Bcrypt Hash", "********", res.hash_value, {"rounds": rounds})
            if not post_result_menu(card, "hasil_bcrypt.txt"):
                break

        else:
            # Verify
            password = safe_input("  Masukkan password: ")
            if not password:
                print(yellow("  [!] Password tidak boleh kosong."))
                continue

            expected = safe_input("  Masukkan hash bcrypt: ")
            if not expected:
                print(yellow("  [!] Hash tidak boleh kosong."))
                continue

            res = bcrypt_verify(password, expected)
            status = "COCOK" if res.match else "TIDAK COCOK"
            card = render_card(
                title="VERIFIKASI BCRYPT",
                method="BCRYPT",
                operation="VERIFY",
                status=status,
                input_text="********",
                output_text=status,
                reasons=res.reasons,
                extra_fields={"Algorithm": "BCRYPT", "Status": status},
            )
            print("\n" + card)
            log_history("Bcrypt Verify", "********", status, {"match": res.match})
            if not post_result_menu(card, "hasil_bcrypt_verify.txt"):
                break


def _handle_random_bytes() -> None:
    """Handle random bytes generation."""
    while True:
        length_input = safe_input("  Panjang random bytes (1-1024) [32]: ")
        try:
            length = int(length_input) if length_input else 32
            if length < 1 or length > 1024:
                print(red("  [!] Panjang harus 1-1024 bytes."))
                continue
        except ValueError:
            print(red("  [!] Panjang harus angka."))
            continue

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title="RANDOM BYTES - Pilih Format Output",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        out = generate_random_bytes(length, encoding=encoding)
        card = render_card(
            title="RANDOM BYTES",
            method="CSPRNG",
            operation="GENERATE",
            status="Berhasil (OK)",
            input_text="",
            output_text=out,
            reasons=["Cryptographically secure random (secrets.token_bytes)"],
            extra_fields={"Length": f"{length} bytes", "Encoding": encoding.upper()},
        )
        print("\n" + card)
        log_history("Random Bytes", "", out, {"length": length, "encoding": encoding})
        if not post_result_menu(card, "hasil_random.txt"):
            break


def handle_rsa() -> None:
    """Interactive handler for RSA Asymmetric Cryptography."""
    while True:
        sel = navigation_menu(
            options=[
                "Generate Key Pair",
                "Encrypt (Public Key)",
                "Decrypt (Private Key)",
                "Sign Message (Private Key)",
                "Verify Signature (Public Key)",
            ],
            title="CRYPTOLAB - RSA ASYMMETRIC CRYPTOGRAPHY",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            if sel == 0:
                _handle_rsa_keygen()
            elif sel == 1:
                _handle_rsa_encrypt()
            elif sel == 2:
                _handle_rsa_decrypt()
            elif sel == 3:
                _handle_rsa_sign()
            elif sel == 4:
                _handle_rsa_verify()
        except BackToMenu:
            continue
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan RSA: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_rsa_keygen() -> None:
    """Handle RSA key pair generation."""
    while True:
        size_sel = navigation_menu(
            options=["1024 bit (Legacy)", "2048 bit (Recommended)", "3072 bit (High Security)", "4096 bit (Maximum)"],
            title="RSA KEYGEN - Pilih Ukuran Kunci",
            back_label="Kembali",
        )
        if size_sel is None:
            break
        key_sizes = [1024, 2048, 3072, 4096]
        key_size = key_sizes[size_sel]

        print(f"\n  Menghasilkan RSA {key_size}-bit key pair...")
        kp = rsa_generate_keypair(key_size)

        print("\n" + DIVIDER)
        print(f"  RSA {key_size}-BIT KEY PAIR GENERATED")
        print(DIVIDER)
        print("\n  PRIVATE KEY (Simpan dengan aman!):")
        print("  " + "\n  ".join(kp.private_key_pem.strip().split("\n")))
        print("\n  PUBLIC KEY (Bisa dibagikan):")
        print("  " + "\n  ".join(kp.public_key_pem.strip().split("\n")))
        print(DIVIDER)

        save_private = safe_input("  Simpan private key ke file? (y/n) [n]: ").lower()
        if save_private in ("y", "ya", "yes"):
            fname = safe_input("  Nama file private key [rsa_private.pem]: ") or "rsa_private.pem"
            with open(fname, "w") as f:
                f.write(kp.private_key_pem)
            print(green(f"  [OK] Private key disimpan ke {fname}"))

        save_public = safe_input("  Simpan public key ke file? (y/n) [n]: ").lower()
        if save_public in ("y", "ya", "yes"):
            fname = safe_input("  Nama file public key [rsa_public.pem]: ") or "rsa_public.pem"
            with open(fname, "w") as f:
                f.write(kp.public_key_pem)
            print(green(f"  [OK] Public key disimpan ke {fname}"))

        log_history(f"RSA KeyGen {key_size}", "", "KEYPAIR GENERATED", {"keysize": key_size})
        if not post_result_menu("", f"hasil_rsa_keygen_{key_size}.txt"):
            break


def _load_key_interactive(prompt: str, is_private: bool) -> str:
    """Load key from file or inline input."""
    print(f"\n  {prompt}")
    print("  [1] Load dari file")
    print("  [2] Paste inline (akhiri dengan baris kosong)")
    src_sel = navigation_menu(
        options=["Load dari file", "Paste inline"],
        title="LOAD KEY",
        back_label="Batal",
    )
    if src_sel is None:
        raise BackToMenu()

    if src_sel == 0:
        filepath = safe_input("  Path file key: ")
        try:
            with open(filepath, "r") as f:
                return f.read().strip()
        except OSError as e:
            print(red(f"  [!] Gagal membaca file: {e}"))
            raise BackToMenu()
    else:
        print("  Paste key (akhiri dengan baris kosong):")
        lines = []
        while True:
            line = input("  ")
            if not line:
                break
            lines.append(line)
        if not lines:
            print(red("  [!] Key tidak boleh kosong."))
            raise BackToMenu()
        return "\n".join(lines)


def _handle_rsa_encrypt() -> None:
    """Handle RSA encryption."""
    while True:
        message = safe_input("  Masukkan plaintext untuk dienkripsi: ")
        if not message:
            print(yellow("  [!] Plaintext tidak boleh kosong."))
            continue

        try:
            pubkey = _load_key_interactive("Load PUBLIC KEY", is_private=False)
        except BackToMenu:
            continue

        pad_sel = navigation_menu(
            options=["OAEP (Recommended)", "PKCS1v15 (Legacy)"],
            title="RSA ENCRYPT - Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        padding = "OAEP" if pad_sel == 0 else "PKCS1v15"

        hash_algo = "SHA256"
        if padding == "OAEP":
            hash_sel = navigation_menu(
                options=["SHA256", "SHA512"],
                title="OAEP - Hash Algorithm",
                back_label="Batal",
            )
            if hash_sel is None:
                continue
            hash_algo = "SHA256" if hash_sel == 0 else "SHA512"

        enc_sel = navigation_menu(
            options=["Hex", "Base64"],
            title="Output Encoding",
            back_label="Batal",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        try:
            res = rsa_encrypt(message, pubkey, padding=padding, hash_algo=hash_algo, encoding=encoding)
            card = render_card(
                title=f"HASIL RSA ENKRIPSI",
                method=f"RSA-{res.algorithm}",
                operation="ENCRYPT",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_text,
                reasons=[f"Key size: {res.key_size} bit", f"Padding: {padding}", f"Encoding: {encoding.upper()}"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            print("\n" + card)
            log_history(f"RSA Encrypt", message, res.output_text, {"algo": res.algorithm})
            if not post_result_menu(card, "hasil_rsa_encrypt.txt"):
                break
        except Exception as e:
            print(red(f"  [!] Enkripsi gagal: {e}"))


def _handle_rsa_decrypt() -> None:
    """Handle RSA decryption."""
    while True:
        ciphertext = safe_input("  Masukkan ciphertext: ")
        if not ciphertext:
            print(yellow("  [!] Ciphertext tidak boleh kosong."))
            continue

        try:
            privkey = _load_key_interactive("Load PRIVATE KEY", is_private=True)
        except BackToMenu:
            continue

        pad_sel = navigation_menu(
            options=["OAEP (Recommended)", "PKCS1v15 (Legacy)"],
            title="RSA DECRYPT - Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        padding = "OAEP" if pad_sel == 0 else "PKCS1v15"

        hash_algo = "SHA256"
        if padding == "OAEP":
            hash_sel = navigation_menu(
                options=["SHA256", "SHA512"],
                title="OAEP - Hash Algorithm",
                back_label="Batal",
            )
            if hash_sel is None:
                continue
            hash_algo = "SHA256" if hash_sel == 0 else "SHA512"

        enc_sel = navigation_menu(
            options=["Hex", "Base64"],
            title="Input Ciphertext Encoding",
            back_label="Batal",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        try:
            res = rsa_decrypt(ciphertext, privkey, padding=padding, hash_algo=hash_algo, encoding=encoding)
            card = render_card(
                title=f"HASIL RSA DEKRIPSI",
                method=f"RSA-{res.algorithm}",
                operation="DECRYPT",
                status="Berhasil (OK)" if not res.is_hex else "Berhasil (Output Hex)",
                input_text=f"[{len(ciphertext)} chars ciphertext]",
                output_text=res.output_text,
                reasons=["UTF-8 valid" if not res.is_hex else "Output bukan UTF-8, ditampilkan hex"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            print("\n" + card)
            log_history(f"RSA Decrypt", ciphertext, res.output_text, {"algo": res.algorithm})
            if not post_result_menu(card, "hasil_rsa_decrypt.txt"):
                break
        except Exception as e:
            print(red(f"  [!] Dekripsi gagal: {e}"))


def _handle_rsa_sign() -> None:
    """Handle RSA signing."""
    while True:
        message = safe_input("  Masukkan pesan untuk ditandatangani: ")
        if not message:
            print(yellow("  [!] Pesan tidak boleh kosong."))
            continue

        try:
            privkey = _load_key_interactive("Load PRIVATE KEY", is_private=True)
        except BackToMenu:
            continue

        pad_sel = navigation_menu(
            options=["PSS (Recommended)", "PKCS1v15 (Legacy)"],
            title="RSA SIGN - Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        sig_padding = "PSS" if pad_sel == 0 else "PKCS1v15"

        hash_sel = navigation_menu(
            options=["SHA256", "SHA512"],
            title="Hash Algorithm",
            back_label="Batal",
        )
        if hash_sel is None:
            continue
        hash_algo = "SHA256" if hash_sel == 0 else "SHA512"

        enc_sel = navigation_menu(
            options=["Hex", "Base64"],
            title="Output Signature Encoding",
            back_label="Batal",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        try:
            res = rsa_sign(message, privkey, padding=sig_padding, hash_algo=hash_algo, encoding=encoding)
            card = render_card(
                title=f"HASIL RSA SIGN",
                method=f"RSA-{res.algorithm}",
                operation="SIGN",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_text,
                reasons=[f"Key size: {res.key_size} bit", f"Hash: {hash_algo}", f"Padding: {sig_padding}"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            print("\n" + card)
            log_history(f"RSA Sign", message, res.output_text, {"algo": res.algorithm})
            if not post_result_menu(card, "hasil_rsa_sign.txt"):
                break
        except Exception as e:
            print(red(f"  [!] Signing gagal: {e}"))


def _handle_rsa_verify() -> None:
    """Handle RSA signature verification."""
    while True:
        message = safe_input("  Masukkan pesan asli: ")
        if not message:
            print(yellow("  [!] Pesan tidak boleh kosong."))
            continue

        signature = safe_input("  Masukkan signature: ")
        if not signature:
            print(yellow("  [!] Signature tidak boleh kosong."))
            continue

        try:
            pubkey = _load_key_interactive("Load PUBLIC KEY", is_private=False)
        except BackToMenu:
            continue

        pad_sel = navigation_menu(
            options=["PSS (Recommended)", "PKCS1v15 (Legacy)"],
            title="RSA VERIFY - Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        sig_padding = "PSS" if pad_sel == 0 else "PKCS1v15"

        hash_sel = navigation_menu(
            options=["SHA256", "SHA512"],
            title="Hash Algorithm",
            back_label="Batal",
        )
        if hash_sel is None:
            continue
        hash_algo = "SHA256" if hash_sel == 0 else "SHA512"

        enc_sel = navigation_menu(
            options=["Hex", "Base64"],
            title="Signature Encoding",
            back_label="Batal",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        try:
            res = rsa_verify(message, signature, pubkey, padding=sig_padding, hash_algo=hash_algo, encoding=encoding)
            status = "VALID (SAH)" if "VALID" in res.output_text else "INVALID (TIDAK SAH)"
            card = render_card(
                title=f"VERIFIKASI RSA SIGNATURE",
                method=f"RSA-{res.algorithm}",
                operation="VERIFY",
                status=status,
                input_text=message,
                output_text=res.output_text,
                reasons=["Verifikasi berhasil" if "VALID" in res.output_text else "Tanda tangan tidak cocok"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": status},
            )
            print("\n" + card)
            log_history(f"RSA Verify", message, res.output_text, {"algo": res.algorithm})
            if not post_result_menu(card, "hasil_rsa_verify.txt"):
                break
        except Exception as e:
            print(red(f"  [!] Verifikasi gagal: {e}"))


def handle_dh() -> None:
    """Interactive handler for Diffie-Hellman Key Exchange."""
    while True:
        sel = navigation_menu(
            options=[
                "Simulasi Key Exchange (Alice & Bob)",
                "Derive Key dari Shared Secret",
            ],
            title="CRYPTOLAB - DIFFIE-HELLMAN KEY EXCHANGE",
            back_label="Kembali ke Menu Utama",
        )
        if sel is None:
            break

        try:
            if sel == 0:
                _handle_dh_exchange()
            elif sel == 1:
                _handle_dh_derive()
        except BackToMenu:
            continue
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan DH: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_dh_exchange() -> None:
    """Handle DH key exchange simulation."""
    while True:
        size_sel = navigation_menu(
            options=["2048 bit (Group 14)", "3072 bit (Group 15)", "4096 bit (Group 16)"],
            title="DHKE - Pilih Ukuran Prime",
            back_label="Kembali",
        )
        if size_sel is None:
            break
        bits = [2048, 3072, 4096][size_sel]

        use_custom = safe_input("  Gunakan private key custom? (y/n) [n]: ").lower()
        alice_priv = None
        bob_priv = None
        if use_custom in ("y", "ya", "yes"):
            alice_hex = safe_input("  Alice private key (hex): ")
            bob_hex = safe_input("  Bob private key (hex): ")
            try:
                alice_priv = int(alice_hex, 16) if alice_hex else None
                bob_priv = int(bob_hex, 16) if bob_hex else None
            except ValueError:
                print(red("  [!] Private key harus hex valid."))
                continue

        res = dh_key_exchange(bits, alice_private=alice_priv, bob_private=bob_priv)

        output = (
            f"Prime (p): {res.prime_hex[:64]}... ({len(res.prime_hex)} hex chars)\n"
            f"Generator (g): {res.generator}\n\n"
            f"Alice Private: {res.alice_private_hex}\n"
            f"Alice Public:  {res.alice_public_hex}\n\n"
            f"Bob Private:   {res.bob_private_hex}\n"
            f"Bob Public:    {res.bob_public_hex}\n\n"
            f"SHARED SECRET: {res.shared_secret_hex}"
        )
        print("\n" + DIVIDER)
        print(f"  DHKE {bits}-BIT KEY EXCHANGE")
        print(DIVIDER)
        print(output)
        print(DIVIDER)

        derive = safe_input("  Derive symmetric key dari shared secret? (y/n) [n]: ").lower()
        if derive in ("y", "ya", "yes"):
            keylen = safe_input("  Key length (bytes) [16]: ") or "16"
            try:
                kl = int(keylen)
                derived = dh_derive_key(res.shared_secret_hex, key_length=kl)
                print(f"\n  Derived Key ({kl} bytes): {derived}")
            except Exception as e:
                print(red(f"  [!] Gagal derive: {e}"))

        log_history(f"DHKE {bits}", "", "EXCHANGE COMPLETE", {"bits": bits})
        if not post_result_menu("", f"hasil_dh_{bits}.txt"):
            break


def _handle_dh_derive() -> None:
    """Handle DH key derivation."""
    while True:
        shared = safe_input("  Masukkan shared secret (hex): ")
        if not shared:
            print(yellow("  [!] Shared secret tidak boleh kosong."))
            continue

        keylen = safe_input("  Key length (bytes) [32]: ") or "32"
        try:
            kl = int(keylen)
        except ValueError:
            print(red("  [!] Key length harus angka."))
            continue

        hash_sel = navigation_menu(
            options=["SHA256", "SHA512"],
            title="Key Derivation - Hash Algorithm",
            back_label="Batal",
        )
        if hash_sel is None:
            continue
        hash_algo = "SHA256" if hash_sel == 0 else "SHA512"

        enc_sel = navigation_menu(
            options=["Hex", "Base64"],
            title="Output Encoding",
            back_label="Batal",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        try:
            derived = dh_derive_key(shared, key_length=kl, hash_algo=hash_algo)
            if encoding == "base64":
                import base64
                derived = base64.b64encode(bytes.fromhex(derived)).decode("ascii")
            card = render_card(
                title="DHKE KEY DERIVATION",
                method=f"HKDF-{hash_algo}",
                operation="DERIVE",
                status="Berhasil (OK)",
                input_text=f"Shared Secret: {shared[:32]}...",
                output_text=derived,
                reasons=[f"Key length: {kl} bytes", f"Hash: {hash_algo}"],
                extra_fields={"Key Length": f"{kl} bytes", "Hash": hash_algo, "Encoding": encoding.upper()},
            )
            print("\n" + card)
            log_history("DHKE Derive", shared, derived, {"keylen": kl, "hash": hash_algo})
            if not post_result_menu(card, "hasil_dh_derive.txt"):
                break
        except Exception as e:
            print(red(f"  [!] Derive gagal: {e}"))


def handle_aes() -> None:
    """Interactive handler for AES (Advanced Encryption Standard - 128 bit CBC/ECB)."""
    while True:
        # Main AES Menu with arrow key navigation
        sel = navigation_menu(
            options=[
                "Dekripsi (Ciphertext Hex -> Plaintext)",
                "Enkripsi (Plaintext -> Ciphertext Hex)",
                "Auto Analisis Mode & Padding (Uji CBC & ECB)",
            ],
            title="CRYPTOLAB - AES (ADVANCED ENCRYPTION STANDARD - 128 BIT)",
            back_label="Kembali ke Menu Utama",
        )
        
        if sel is None:
            break
        
        try:
            if sel == 0:
                # Dekripsi AES
                _handle_aes_decrypt()
            elif sel == 1:
                # Enkripsi AES
                _handle_aes_encrypt()
            elif sel == 2:
                # Auto Analisis
                _handle_aes_auto_analyze()
        
        except BackToMenu:
            continue
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan AES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_aes_decrypt() -> None:
    """Handle AES decryption with mode selection."""
    while True:
        print("\n" + DIVIDER)
        print("  AES DEKRIPSI - Pilih Mode")
        print(DIVIDER)
        
        mode_sel = navigation_menu(
            options=[
                "Auto (analisis heuristik mode dan padding yang valid, key & IV opsional)",
                "CBC (Cipher Block Chaining - membutuhkan IV 16 byte)",
                "ECB (Electronic Codebook - tanpa IV)",
            ],
            title="AES DEKRIPSI - Pilih Mode",
            back_label="Kembali ke Menu AES",
        )
        
        if mode_sel is None:
            break
        
        try:
            ct_hex = safe_input("  Masukkan ciphertext (format heksadesimal): ")
            if not ct_hex:
                print(yellow("  [!] Ciphertext heksadesimal tidak boleh kosong."))
                continue

            clean_hex = re.sub(r"\s+", "", ct_hex)
            if len(clean_hex) % 32 != 0:
                print(yellow(
                    f"  [Perhatian] Panjang ciphertext ({len(clean_hex)} hex) bukan kelipatan ukuran blok AES (32 hex / 16 byte)."
                ))

            if mode_sel == 0:
                # Auto mode - key and IV are optional
                print("\n  Mode Auto: Key dan IV opsional (tekan Enter untuk melewati)")
                key = safe_input("  Masukkan key (tepat 16 karakter/byte, Enter untuk skip): ")
                key_val = key if len(key.encode("utf-8")) == 16 else None
                
                iv = None
                if key_val:
                    iv_cand = safe_input("  Masukkan IV (16 karakter untuk CBC, Enter untuk skip/ECB): ")
                    iv = iv_cand if len(iv_cand.encode("utf-8")) == 16 else None
                
                if key_val is None:
                    print(yellow("  [!] Key dilewati. Auto analisis memerlukan key. Gunakan mode CBC/ECB manual."))
                    continue

                candidates: List[AesResult] = aes_auto_analyze(ct_hex, key=key_val, iv=iv)

                if not candidates:
                    print(yellow("  [!] Tidak ada konfigurasi AES yang berhasil secara teknis."))
                    continue

                top = candidates[0]
                card = render_card(
                    title="HASIL ANALISIS AES (KANDIDAT TERBAIK)",
                    method=f"AES-128 ({top.mode}, Padding {top.padding})",
                    operation="Dekripsi",
                    status="Kandidat ditemukan" if top.readable_success else "Dekripsi teknis berhasil (Plaintext belum terverifikasi)",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={
                        "Mode": top.mode,
                        "Padding": top.padding,
                        "Status UTF-8": "Valid" if top.is_utf8 else "Non-UTF8 (Tampil Hex)",
                    },
                )
                print("\n" + card)

                if len(candidates) > 1:
                    print("\n  KANDIDAT MODE/PADDING LAIN:")
                    print("  ------------------------------------------------------------------")
                    for idx, c in enumerate(candidates[1:], start=1):
                        prev = c.output_text[:35] + ("..." if len(c.output_text) > 35 else "")
                        print(f"  [{idx}] Mode {c.mode} | Padding {c.padding} | Skor: {c.score:.1f}/100 -> {prev}")

                print(THIN_DIVIDER)
                print("  Catatan: Ciphertext heksadesimal tidak membuktikan mode CBC atau ECB.")
                print("  Hasil ditampilkan sebagai kandidat heuristik terverifikasi.")
                print(DIVIDER)

                log_history("AES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                if not post_result_menu(card, "hasil_aes.txt"):
                    break

            else:
                mode = "CBC" if mode_sel == 1 else "ECB"
                key = safe_input("  Masukkan key (tepat 16 karakter/byte): ")
                if len(key.encode("utf-8")) != 16:
                    print(red(f"  [!] Panjang key AES-128 harus tepat 16 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
                    continue

                iv: Optional[str] = None
                if mode == "CBC":
                    iv = safe_input("  Masukkan IV (tepat 16 karakter/byte): ")
                    if len(iv.encode("utf-8")) != 16:
                        print(red(f"  [!] Panjang IV AES CBC harus tepat 16 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)."))
                        continue

                print("  Pilih padding:")
                pad_sel = navigation_menu(
                    options=["PKCS#7 (standar default)", "Tanpa Padding (None)"],
                    title="AES DEKRIPSI - Pilih Padding",
                    back_label="Batal",
                )
                if pad_sel is None:
                    continue
                padding = "PKCS7" if pad_sel == 0 else "None"

                res = aes_decrypt(ct_hex, key=key, mode=mode, iv=iv, padding=padding)

                status_msg = "Berhasil (Teks UTF-8 Terbaca)" if res.readable_success else "Berhasil Secara Teknis (Keterbacaan Rendah)"
                if not res.is_utf8:
                    status_msg = "Berhasil Secara Teknis (Bukan teks UTF-8 valid - Hasil berupa Hex)"

                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB - AES DECRYPT",
                    method=f"AES-128 ({mode})",
                    operation="Dekripsi",
                    status=status_msg,
                    input_text=ct_hex,
                    output_text=res.output_text if res.is_utf8 else f"[Bytes Hex] {res.output_text}",
                    reasons=res.reasons,
                    extra_fields={
                        "Mode": mode,
                        "Padding": padding,
                        "Status UTF-8": "Valid" if res.is_utf8 else "Non-UTF8 (Tampil Hex)",
                    },
                )
                print("\n" + card)

                log_history("AES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                if not post_result_menu(card, "hasil_aes.txt"):
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan AES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def _handle_aes_encrypt() -> None:
    """Handle AES encryption."""
    while True:
        plaintext = safe_input("  Masukkan plaintext untuk dienkripsi: ")
        if not plaintext:
            print(yellow("  [!] Plaintext tidak boleh kosong."))
            continue

        mode_sel = navigation_menu(
            options=[
                "CBC (Cipher Block Chaining - membutuhkan IV 16 byte) [Default]",
                "ECB (Electronic Codebook - tanpa IV)",
            ],
            title="AES ENKRIPSI - Pilih Mode",
            back_label="Batal",
        )
        if mode_sel is None:
            break
        
        mode = "CBC" if mode_sel == 0 else "ECB"

        key = safe_input("  Masukkan key (tepat 16 karakter/byte): ")
        if len(key.encode("utf-8")) != 16:
            print(red(f"  [!] Panjang key AES-128 harus tepat 16 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
            continue

        iv = None
        if mode == "CBC":
            iv = safe_input("  Masukkan IV (tepat 16 karakter/byte): ")
            if len(iv.encode("utf-8")) != 16:
                print(red(f"  [!] Panjang IV AES CBC harus tepat 16 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)."))
                continue

        pad_sel = navigation_menu(
            options=["PKCS#7 (standar default)", "Tanpa Padding (None - plaintext harus kelipatan 16 byte)"],
            title="AES ENKRIPSI - Pilih Padding",
            back_label="Batal",
        )
        if pad_sel is None:
            continue
        padding = "PKCS7" if pad_sel == 0 else "None"

        res_enc = aes_encrypt(plaintext, key=key, mode=mode, iv=iv, padding=padding)

        card = render_card(
            title="HASIL OPERASI CRYPTOLAB - AES ENCRYPT",
            method=f"AES-128 ({mode})",
            operation="Enkripsi",
            status="Berhasil (OK)",
            input_text=plaintext,
            output_text=res_enc.output_text,
            reasons=["Enkripsi selesai tanpa kesalahan"],
            extra_fields={"Mode": mode, "Padding": padding},
        )
        print("\n" + card)

        log_history("AES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

        if not post_result_menu(card, "hasil_aes_encrypt.txt"):
            break


def _handle_aes_auto_analyze() -> None:
    """Handle AES auto analyze."""
    while True:
        print("\n" + DIVIDER)
        print("  AES AUTO ANALISIS")
        print(DIVIDER)
        print("  Fitur ini menguji kombinasi mode (CBC/ECB) dan padding (PKCS7/None)")
        print("  Key diperlukan, IV opsional (tekan Enter untuk melewati).")
        print(THIN_DIVIDER)

        try:
            ct_hex = safe_input("  Masukkan ciphertext heksadesimal: ")
            if not ct_hex:
                print(yellow("  [!] Ciphertext tidak boleh kosong."))
                continue

            key = safe_input("  Masukkan key (tepat 16 karakter/byte, Enter untuk skip): ")
            key_val = key if len(key.encode("utf-8")) == 16 else None
            
            iv_val: Optional[str] = None
            if key_val:
                iv_cand = safe_input("  Masukkan IV (16 karakter untuk CBC, Enter untuk skip): ")
                iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 16 else None
            
            if key_val is None:
                print(yellow("  [!] Key dilewati. AES tidak dapat didekripsi tanpa key."))
                continue

            candidates = aes_auto_analyze(ct_hex, key=key_val, iv=iv_val)

            if candidates:
                top = candidates[0]
                card = render_card(
                    title="HASIL ANALISIS AES",
                    method=f"AES-128 ({top.mode}, Padding {top.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={"Mode": top.mode, "Padding": top.padding},
                )
                print("\n" + card)
                log_history("AES Auto Analyze", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})
                if not post_result_menu(card, "hasil_aes_auto.txt"):
                    break
            else:
                print(yellow("  [!] Tidak ada kombinasi AES yang valid dengan parameter tersebut."))

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan AES: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_base64() -> None:
    """Interactive handler for Base64 codec."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - BASE64 CODEC")
        print(DIVIDER)
        print("  Catatan: Base64 adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(THIN_DIVIDER)
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Base64)", "Decode (Base64 -> Teks UTF-8)"],
            title="CRYPTOLAB - BASE64 CODEC",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            op_name = "Encode" if choice == 0 else "Decode"
            data = safe_input(f"  Masukkan data untuk Base64 {op_name.lower()}: ")
            if not data:
                print(yellow("  [!] Data tidak boleh kosong."))
                continue

            if choice == 0:
                out = base64_encode(data)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Base64",
                    operation="Encode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Data di-encode ke representasi Base64 ASCII."],
                    extra_fields={"Kategori": "Encoding"},
                )
                log_history("Base64 Encode", data, out)
            else:
                out = base64_decode(data)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Base64",
                    operation="Decode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Sintaks Base64 valid dan menghasilkan teks UTF-8 valid."],
                    extra_fields={"Kategori": "Encoding"},
                )
                log_history("Base64 Decode", data, out)

            print("\n" + card)
            if not post_result_menu(card, "hasil_base64.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_hex() -> None:
    """Interactive handler for Hexadecimal codec."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - HEXADECIMAL CODEC")
        print(DIVIDER)
        print("  Catatan: Hexadecimal adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(THIN_DIVIDER)
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Hex)", "Decode (Hex -> Teks UTF-8)"],
            title="CRYPTOLAB - HEXADECIMAL CODEC",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice == 0:
                data = safe_input("  Masukkan teks untuk di-encode ke Hex: ")
                if not data:
                    print(yellow("  [!] Teks tidak boleh kosong."))
                    continue

                delim = safe_input("  Pemisah byte (default: spasi, ketik '' untuk tanpa spasi): ")
                delimiter = " " if delim == "" else delim

                out = hex_encode(data, delimiter=delimiter)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Hexadecimal",
                    operation="Encode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Data di-encode ke pasangan byte heksadesimal."],
                    extra_fields={"Kategori": "Encoding", "Pemisah": repr(delimiter)},
                )
                log_history("Hex Encode", data, out, {"delimiter": delimiter})
            else:
                data = safe_input("  Masukkan string heksadesimal untuk di-decode: ")
                if not data:
                    print(yellow("  [!] Data heksadesimal tidak boleh kosong."))
                    continue

                out = hex_decode(data)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Hexadecimal",
                    operation="Decode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Pasangan byte heksadesimal valid berhasil di-decode ke teks UTF-8."],
                    extra_fields={"Kategori": "Encoding"},
                )
                log_history("Hex Decode", data, out)

            print("\n" + card)
            if not post_result_menu(card, "hasil_hex.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_binary() -> None:
    """Interactive handler for Binary codec."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - BINARY CODEC (8-BIT)")
        print(DIVIDER)
        print("  Catatan: Binary adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(THIN_DIVIDER)
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Biner 8-Bit)", "Decode (Biner 8-Bit -> Teks UTF-8)"],
            title="CRYPTOLAB - BINARY CODEC (8-BIT)",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice == 0:
                data = safe_input("  Masukkan teks untuk di-encode ke Biner: ")
                if not data:
                    print(yellow("  [!] Teks tidak boleh kosong."))
                    continue

                delim = safe_input("  Pemisah byte (default: spasi, ketik '' untuk tanpa spasi): ")
                delimiter = " " if delim == "" else delim

                out = binary_encode(data, delimiter=delimiter)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Binary 8-Bit",
                    operation="Encode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Data di-encode ke representasi biner 8-bit per byte."],
                    extra_fields={"Kategori": "Encoding", "Pemisah": repr(delimiter)},
                )
                log_history("Binary Encode", data, out, {"delimiter": delimiter})
            else:
                data = safe_input("  Masukkan string biner untuk di-decode: ")
                if not data:
                    print(yellow("  [!] Data biner tidak boleh kosong."))
                    continue

                out = binary_decode(data)
                card = render_card(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Binary 8-Bit",
                    operation="Decode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Representasi biner 8-bit valid berhasil di-decode ke teks UTF-8."],
                    extra_fields={"Kategori": "Encoding"},
                )
                log_history("Binary Decode", data, out)

            print("\n" + card)
            if not post_result_menu(card, "hasil_binary.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            print(red(f"\n  [!] Kesalahan: {err}"))
        except Exception as err:
            print(red(f"\n  [!] Kesalahan tak terduga: {err}"))


def handle_history() -> None:
    """Interactive handler for viewing and managing local history."""
    while True:
        hist_file = get_history_file()
        records = read_history(limit=20)

        print("\n" + DIVIDER)
        print("  CRYPTOLAB - RIWAYAT ANALISIS & OPERASI LOKAL")
        print(DIVIDER)
        print(f"  Lokasi file riwayat : {hist_file}")
        print(f"  Total catatan aktif : {len(records)} operasi terakhir")
        print(THIN_DIVIDER)

        if not records:
            print("  Belum ada riwayat operasi yang tersimpan.")
            print(DIVIDER)
        else:
            print("  Waktu (UTC)          | Operasi                 | Input -> Output")
            print("  ---------------------+-------------------------+----------------------------------")
            for r in records:
                time_str = r.get("timestamp", "")[:19].replace("T", " ")
                op_str = r.get("operation", "")[:23]
                inp_str = r.get("input", "")[:14]
                out_str = r.get("output", "")[:16]
                preview = f"{inp_str} -> {out_str}"
                print(f"  {time_str:<20} | {op_str:<23} | {preview}")
            print(DIVIDER)

        choice = navigation_menu(
            options=["Bersihkan Seluruh Riwayat", "Kembali ke Menu Utama"],
            title="RIWAYAT - PILIH OPSI",
            back_label="Kembali ke Menu Utama",
        )

        if choice is None or choice == 1:
            break
        elif choice == 0:
            confirm = safe_input("  Yakin ingin menghapus seluruh riwayat? (y/n) [n]: ", allow_back=False).lower()
            if confirm in ("y", "ya", "yes"):
                success = clear_history()
                if success:
                    print(green("  [OK] Riwayat analisis lokal berhasil dibersihkan."))
                else:
                    print(red("  [!] Gagal menghapus file riwayat."))


# ======================================================================
# MENU UTAMA INTERAKTIF
# ======================================================================

def run_interactive_menu() -> None:
    """Run CryptoLab in a dedicated terminal screen when attached to a TTY."""
    use_alt_screen = bool(getattr(sys.stdout, "isatty", lambda: False)())
    if use_alt_screen:
        sys.stdout.write("\033[?1049h\033[2J\033[H")
        sys.stdout.flush()
    try:
        _run_interactive_menu()
    finally:
        if use_alt_screen:
            sys.stdout.write("\033[?1049l")
            sys.stdout.flush()


def _run_interactive_menu() -> None:
    """Run the interactive menu loop inside the active terminal screen."""
    while True:
        sel = navigation_menu(
            options=[
                "Auto Analyze",
                "Caesar Cipher",
                "Vigenere Cipher",
                "Playfair Cipher",
                "Hill Cipher",
                "Affine Cipher",
                "Rail Fence Cipher",
                "DES (Data Encryption Standard - 64 bit)",
                "AES (Advanced Encryption Standard - 128 bit)",
                "RC2 (ARC2 - Legacy 64 bit)",
                "Hashing & Password Security (MD5, SHA, HMAC, PBKDF2, Bcrypt)",
                "RSA Asymmetric Cryptography (KeyGen, Encrypt, Decrypt, Sign, Verify)",
                "Diffie-Hellman Key Exchange (DHKE)",
                "Base64",
                "Hex",
                "Binary",
                "Riwayat",
            ],
            title=f"CRYPTOLAB CLI v{__version__} - TOOLKIT KRIPTOGRAFI & ENCODING",
            back_label="Keluar",
            allow_back=False,
            banner=LOGO,
            banner_responsive=True,
        )

        if sel is None:
            print("\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
            break

        try:
            if sel == 0:
                handle_auto_analyze()
            elif sel == 10:
                handle_history()
                handle_playfair()
            elif sel == 4:
                handle_hill()
            elif sel == 5:
                handle_affine()
            elif sel == 6:
                handle_railfence()
            elif sel == 7:
                handle_des()
            elif sel == 8:
                handle_aes()
            elif sel == 9:
                handle_rc2()
            elif sel == 10:
                handle_hashing()
            elif sel == 11:
                handle_rsa()
            elif sel == 12:
                handle_dh()
            elif sel == 13:
                handle_base64()
            elif sel == 14:
                handle_hex()
            elif sel == 15:
                handle_binary()
            elif sel == 16:
                handle_history()
            elif sel == 17:
                print("\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
                break
        except BackToMenu:
            continue


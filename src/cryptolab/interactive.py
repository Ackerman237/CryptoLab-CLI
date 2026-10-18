"""Interactive Terminal Interface for CryptoLab CLI.

Provides a professional, beginner-friendly menu in Bahasa Indonesia
with clear prompts, input validation, back navigation, and consistent formatting.
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
from cryptolab.analysis.auto_engine import run_auto_analysis, AutoAnalysisReport, AutoCandidate
from cryptolab.analysis.brute_force import caesar_brute_force, find_best_candidate, CaesarCandidate
from cryptolab.utils.history import log_history, read_history, clear_history, get_history_file

DIVIDER = "=" * 68
THIN_DIVIDER = "-" * 68


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
    """Render consistent result card matching the required lab format."""
    lines = [
        DIVIDER,
        f"  {title.upper()}",
        DIVIDER,
        f"  Metode       : {method}",
        f"  Operasi      : {operation}",
        f"  Status       : {status}",
    ]

    if extra_fields:
        for k, v in extra_fields.items():
            lines.append(f"  {k:<12} : {v}")

    # Format input and output cleanly
    lines.extend([
        THIN_DIVIDER,
        "  INPUT        :",
        f"  {input_text}",
        THIN_DIVIDER,
        "  OUTPUT       :",
        f"  {output_text}",
    ])

    if reasons:
        lines.append(THIN_DIVIDER)
        lines.append(f"  Alasan       : {'; '.join(reasons)}")

    lines.append(DIVIDER)
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
        print("\n  Opsi Setelah Proses:")
        print("  [1] Ulangi proses / Coba data lain")
        print("  [2] Simpan hasil ke file")
        print("  [0] Kembali ke menu utama")
        choice = safe_input("  Pilih opsi [0-2] [0]: ", allow_back=True)
        if choice in ("0", "", "b", "kembali"):
            return False
        elif choice == "1":
            return True
        elif choice == "2":
            save_result_prompt(result_text, default_filename)
        else:
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 0, 1, atau 2."))


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
        print("  [1] Enkripsi (Plaintext -> Ciphertext)")
        print("  [2] Dekripsi (Ciphertext -> Plaintext dengan Shift Diketahui)")
        print("  [3] Brute Force (Uji Seluruh 26 Pergeseran / Cari Shift Otomatis)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-3]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break


        if choice not in ("1", "2", "3"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih nomor 0-3."))
            continue

        try:
            if choice in ("1", "2"):
                op_name = "Enkripsi" if choice == "1" else "Dekripsi"
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

                if choice == "1":
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

            elif choice == "3":
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
        print("  [1] Enkripsi (Plaintext -> Ciphertext)")
        print("  [2] Dekripsi (Ciphertext -> Plaintext)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-2]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break


        if choice not in ("1", "2"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 1, 2, atau 0."))
            continue

        try:
            op_name = "Enkripsi" if choice == "1" else "Dekripsi"
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

            if choice == "1":
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


def handle_des() -> None:
    """Interactive handler for DES (CBC/ECB)."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - DES (DATA ENCRYPTION STANDARD)")
        print(DIVIDER)
        print("  Perhatian Keamanan:")
        print("  DES menggunakan panjang kunci 56-bit yang sudah usang dan rentan brute-force.")
        print("  Fitur ini disediakan strictly untuk pembelajaran lab dan tantangan CTF.")
        print(THIN_DIVIDER)
        print("  Pilih Operasi:")
        print("  [1] Dekripsi (Ciphertext Hex -> Plaintext)")
        print("  [2] Enkripsi (Plaintext -> Ciphertext Hex)")
        print("  [3] Auto Analisis Mode & Padding (Uji ECB & CBC)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-3]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break


        if choice not in ("1", "2", "3"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih nomor 0-3."))
            continue

        try:
            if choice == "1":
                # Dekripsi DES
                ct_hex = safe_input("  Masukkan ciphertext (format heksadesimal): ")
                if not ct_hex:
                    print(yellow("  [!] Ciphertext heksadesimal tidak boleh kosong."))
                    continue

                print("\n  Pilih Mode DES:")
                print("  [1] Auto (analisis mode dan parameter yang memungkinkan)")
                print("  [2] CBC (Cipher Block Chaining - membutuhkan IV)")
                print("  [3] ECB (Electronic Codebook - tanpa IV)")
                print("  [0] Batal")
                mode_choice = safe_input("  Pilih mode [1-3] [1]: ") or "1"

                if mode_choice in ("0", "b"):
                    continue

                if mode_choice == "1":
                    # Mode Auto
                    key = safe_input("  Masukkan key (tepat 8 karakter/byte): ")
                    if len(key.encode("utf-8")) != 8:
                        print(red(f"  [!] Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
                        continue

                    iv_cand = safe_input(
                        "  Masukkan IV (8 karakter untuk mode CBC, atau tekan Enter jika tanpa IV): "
                    )
                    iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 8 else None

                    candidates: List[DesResult] = des_auto_analyze(ct_hex, key=key, iv=iv_val)

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
                    print("  Hasil ditampilkan sebagai kandidat heuristik, bukan kepastian mutlak.")
                    print(DIVIDER)

                    # Do NOT log secret key/IV
                    log_history("DES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                    if not post_result_menu(card, "hasil_des.txt"):
                        break

                elif mode_choice in ("2", "3"):
                    mode = "CBC" if mode_choice == "2" else "ECB"
                    key = safe_input("  Masukkan key: ")
                    if len(key.encode("utf-8")) != 8:
                        print(red(f"  [!] Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
                        continue

                    iv: Optional[str] = None
                    if mode == "CBC":
                        iv = safe_input("  Masukkan IV: ")
                        if len(iv.encode("utf-8")) != 8:
                            print(red(f"  [!] Panjang IV DES CBC harus tepat 8 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)."))
                            continue

                    print("  Pilih padding:")
                    print("  [1] PKCS#7 (standar default)")
                    print("  [2] Tanpa Padding (None)")
                    pad_choice = safe_input("  Pilih padding [1-2] [1]: ") or "1"
                    padding = "PKCS7" if pad_choice == "1" else "None"

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

                    # Do NOT log secret key/IV
                    log_history("DES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                    if not post_result_menu(card, "hasil_des.txt"):
                        break

            elif choice == "2":
                # Enkripsi DES
                plaintext = safe_input("  Masukkan plaintext untuk dienkripsi: ")
                if not plaintext:
                    print(yellow("  [!] Plaintext tidak boleh kosong."))
                    continue

                print("\n  Pilih Mode DES:")
                print("  [1] CBC (Cipher Block Chaining - membutuhkan IV) [Default]")
                print("  [2] ECB (Electronic Codebook - tanpa IV)")
                mode_c = safe_input("  Pilih mode [1-2] [1]: ") or "1"
                mode = "CBC" if mode_c == "1" else "ECB"

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

                print("  Pilih padding:")
                print("  [1] PKCS#7 (standar default)")
                print("  [2] Tanpa Padding (None - plaintext harus kelipatan 8 byte)")
                pad_c = safe_input("  Pilih padding [1-2] [1]: ") or "1"
                padding = "PKCS7" if pad_c == "1" else "None"

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

                # Do NOT log secret key/IV
                log_history("DES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

                if not post_result_menu(card, "hasil_des_encrypt.txt"):
                    break

            elif choice == "3":
                # Langsung ke Auto Analisis DES
                ct_hex = safe_input("  Masukkan ciphertext heksadesimal: ")
                key = safe_input("  Masukkan key jika tersedia, atau tekan Enter untuk melewati: ")
                iv_input = safe_input("  Masukkan IV jika tersedia (khusus CBC), atau tekan Enter untuk melewati: ")

                if not key:
                    print(yellow("  [!] DES tidak dapat didekripsi tanpa key. Silakan peroleh key dari challenge lab."))
                    continue

                iv_val = iv_input if len(iv_input.encode("utf-8")) == 8 else None
                candidates = des_auto_analyze(ct_hex, key=key, iv=iv_val)

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


def handle_aes() -> None:
    """Interactive handler for AES (Advanced Encryption Standard - 128 bit CBC/ECB)."""
    while True:
        print("\n" + DIVIDER)
        print("  CRYPTOLAB - AES (ADVANCED ENCRYPTION STANDARD - 128 BIT)")
        print(DIVIDER)
        print("  Catatan Kriptografi:")
        print("  AES adalah standar enkripsi simetris modern (FIPS 197) dengan ukuran")
        print("  blok 128-bit (16 byte). AES-128 membutuhkan key sepanjang tepat 16 byte.")
        print(THIN_DIVIDER)
        print("  Pilih Operasi:")
        print("  [1] Dekripsi (Ciphertext Hex -> Plaintext)")
        print("  [2] Enkripsi (Plaintext -> Ciphertext Hex)")
        print("  [3] Auto Analisis Mode & Padding (Uji CBC & ECB)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-3]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break

        if choice not in ("1", "2", "3"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih nomor 0-3."))
            continue

        try:
            if choice == "1":
                # Dekripsi AES
                ct_hex = safe_input("  Masukkan ciphertext (format heksadesimal): ")
                if not ct_hex:
                    print(yellow("  [!] Ciphertext heksadesimal tidak boleh kosong."))
                    continue

                clean_hex = re.sub(r"\s+", "", ct_hex)
                if len(clean_hex) % 32 != 0:
                    print(yellow(
                        f"  [Perhatian] Panjang ciphertext ({len(clean_hex)} hex) bukan kelipatan ukuran blok AES (32 hex / 16 byte)."
                    ))

                print("\n  Pilih Mode AES:")
                print("  [1] Auto (analisis heuristik mode dan padding yang valid)")
                print("  [2] CBC (Cipher Block Chaining - membutuhkan IV 16 byte)")
                print("  [3] ECB (Electronic Codebook - tanpa IV)")
                print("  [0] Batal")
                mode_choice = safe_input("  Pilih mode [1-3] [1]: ") or "1"

                if mode_choice in ("0", "b"):
                    continue

                if mode_choice == "1":
                    # Mode Auto
                    key = safe_input("  Masukkan key (tepat 16 karakter/byte): ")
                    if len(key.encode("utf-8")) != 16:
                        print(red(f"  [!] Panjang key AES-128 harus tepat 16 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)."))
                        continue

                    iv_cand = safe_input(
                        "  Masukkan IV (16 karakter untuk mode CBC, atau tekan Enter jika tanpa IV): "
                    )
                    iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 16 else None

                    candidates: List[AesResult] = aes_auto_analyze(ct_hex, key=key, iv=iv_val)

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

                    # Do NOT log secret key/IV
                    log_history("AES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                    if not post_result_menu(card, "hasil_aes.txt"):
                        break

                elif mode_choice in ("2", "3"):
                    mode = "CBC" if mode_choice == "2" else "ECB"
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
                    print("  [1] PKCS#7 (standar default)")
                    print("  [2] Tanpa Padding (None)")
                    pad_choice = safe_input("  Pilih padding [1-2] [1]: ") or "1"
                    padding = "PKCS7" if pad_choice == "1" else "None"

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

                    # Do NOT log secret key/IV
                    log_history("AES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                    if not post_result_menu(card, "hasil_aes.txt"):
                        break

            elif choice == "2":
                # Enkripsi AES
                plaintext = safe_input("  Masukkan plaintext untuk dienkripsi: ")
                if not plaintext:
                    print(yellow("  [!] Plaintext tidak boleh kosong."))
                    continue

                print("\n  Pilih Mode AES:")
                print("  [1] CBC (Cipher Block Chaining - membutuhkan IV 16 byte) [Default]")
                print("  [2] ECB (Electronic Codebook - tanpa IV)")
                mode_c = safe_input("  Pilih mode [1-2] [1]: ") or "1"
                mode = "CBC" if mode_c == "1" else "ECB"

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

                print("  Pilih padding:")
                print("  [1] PKCS#7 (standar default)")
                print("  [2] Tanpa Padding (None - plaintext harus kelipatan 16 byte)")
                pad_c = safe_input("  Pilih padding [1-2] [1]: ") or "1"
                padding = "PKCS7" if pad_c == "1" else "None"

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

                # Do NOT log secret key/IV
                log_history("AES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

                if not post_result_menu(card, "hasil_aes_encrypt.txt"):
                    break

            elif choice == "3":
                # Langsung ke Auto Analisis AES
                ct_hex = safe_input("  Masukkan ciphertext heksadesimal: ")
                key = safe_input("  Masukkan key jika tersedia, atau tekan Enter untuk melewati: ")
                iv_input = safe_input("  Masukkan IV jika tersedia (khusus CBC), atau tekan Enter untuk melewati: ")

                if not key:
                    print(yellow("  [!] AES tidak dapat didekripsi tanpa key. Silakan peroleh key dari challenge lab."))
                    continue

                iv_val = iv_input if len(iv_input.encode("utf-8")) == 16 else None
                candidates = aes_auto_analyze(ct_hex, key=key, iv=iv_val)

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
        print("  [1] Encode (Teks UTF-8 -> Base64)")
        print("  [2] Decode (Base64 -> Teks UTF-8)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-2]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break


        if choice not in ("1", "2"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 1, 2, atau 0."))
            continue

        try:
            op_name = "Encode" if choice == "1" else "Decode"
            data = safe_input(f"  Masukkan data untuk Base64 {op_name.lower()}: ")
            if not data:
                print(yellow("  [!] Data tidak boleh kosong."))
                continue

            if choice == "1":
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
        print("  [1] Encode (Teks UTF-8 -> Hex)")
        print("  [2] Decode (Hex -> Teks UTF-8)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-2]: ", allow_back=False)
        if choice in ("0", "b", "kembali"):
            break


        if choice not in ("1", "2"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 1, 2, atau 0."))
            continue

        try:
            if choice == "1":
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
        print("  [1] Encode (Teks UTF-8 -> Biner 8-Bit)")
        print("  [2] Decode (Biner 8-Bit -> Teks UTF-8)")
        print("  [0] Kembali ke Menu Utama")
        print(DIVIDER)

        choice = safe_input("  Pilih operasi [0-2]: ")
        if choice in ("0", "b", "kembali"):
            break

        if choice not in ("1", "2"):
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 1, 2, atau 0."))
            continue

        try:
            if choice == "1":
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

        print("  Opsi:")
        print("  [1] Bersihkan Seluruh Riwayat")
        print("  [0] Kembali ke Menu Utama")
        choice = safe_input("  Pilih opsi [0-1] [0]: ", allow_back=True)

        if choice in ("0", "", "b", "kembali"):
            break
        elif choice == "1":
            confirm = safe_input("  Yakin ingin menghapus seluruh riwayat? (y/n) [n]: ", allow_back=False).lower()
            if confirm in ("y", "ya", "yes"):
                success = clear_history()
                if success:
                    print(green("  [OK] Riwayat analisis lokal berhasil dibersihkan."))
                else:
                    print(red("  [!] Gagal menghapus file riwayat."))
        else:
            print(yellow("  [!] Pilihan tidak valid. Silakan pilih 0 atau 1."))


# ======================================================================
# MENU UTAMA INTERAKTIF
# ======================================================================

def run_interactive_menu() -> None:
    """Run interactive terminal menu for CryptoLab."""
    while True:
        print("\n" + DIVIDER)
        print(bold(f"  CRYPTOLAB CLI v{__version__} - TOOLKIT KRIPTOGRAFI & ENCODING"))
        print(DIVIDER)
        print("  [1] Auto Analyze")
        print("  [2] Caesar Cipher")
        print("  [3] Vigenere Cipher")
        print("  [4] DES (Data Encryption Standard - 64 bit)")
        print("  [5] AES (Advanced Encryption Standard - 128 bit)")
        print("  [6] Base64")
        print("  [7] Hex")
        print("  [8] Binary")
        print("  [9] Riwayat")
        print("  [0] Keluar (atau '10')")
        print(DIVIDER)

        try:
            choice = safe_input("  Pilih menu [0-9]: ", allow_back=False)
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
            break

        if choice in ("0", "10", "q", "keluar", "exit"):
            print("\n  Terima kasih telah menggunakan CryptoLab CLI. Sampai jumpa!\n")
            break

        try:
            if choice == "1":
                handle_auto_analyze()
            elif choice == "2":
                handle_caesar()
            elif choice == "3":
                handle_vigenere()
            elif choice == "4":
                handle_des()
            elif choice == "5":
                handle_aes()
            elif choice == "6":
                handle_base64()
            elif choice == "7":
                handle_hex()
            elif choice == "8":
                handle_binary()
            elif choice == "9":
                handle_history()
            else:
                print(yellow("  [!] Pilihan tidak valid. Silakan masukkan nomor antara 0 dan 9 (atau 10/q untuk keluar)."))
        except BackToMenu:
            continue


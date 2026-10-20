"""Classical cipher interactive handlers (Caesar, Vigenere, Playfair, Hill, Affine, Rail Fence)."""

import sys
from typing import List, Optional

import readchar
from readchar import key as readchar_key

from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.classical.playfair import playfair_encrypt, playfair_decrypt
from cryptolab.classical.hill import hill_encrypt, hill_decrypt
from cryptolab.classical.affine import affine_encrypt, affine_decrypt, affine_brute_force, VALID_A_VALUES
from cryptolab.classical.railfence import railfence_encrypt, railfence_decrypt, railfence_brute_force

from cryptolab.analysis.brute_force import caesar_brute_force, find_best_candidate, CaesarCandidate

from cryptolab.exceptions import CryptoLabError, InvalidKeyError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, Menu, navigation_menu,
    BackToMenu, hide_cursor, show_cursor,
    HINTS_MAIN, HINTS_SUB,
)


def handle_caesar() -> None:
    """Interactive handler for Caesar Cipher."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - CAESAR CIPHER")
        print(Rule.heavy())
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
                text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
                if not text:
                    Message.warning("Teks tidak boleh kosong")
                    continue

                shift = Prompt.ask_int("Masukkan nilai shift (bilangan bulat)")
                if shift is None:
                    continue

                if choice == 0:
                    out = caesar_encrypt(text, shift)
                    card = Panel.result(
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
                    card = Panel.result(
                        title="HASIL OPERASI CRYPTOLAB",
                        method="Caesar Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=out,
                        extra_fields={"Shift": str(shift)},
                    )
                    log_history("Caesar Decrypt", text, out, {"shift": shift})

                Panel.display(card)
                if not _post_result_menu(card, "hasil_caesar.txt"):
                    break

            elif choice == 2:
                text = Prompt.ask("Masukkan ciphertext Caesar")
                if not text:
                    Message.warning("Ciphertext tidak boleh kosong")
                    continue

                candidates = caesar_brute_force(text)
                best = find_best_candidate(candidates)

                view_opt = Prompt.ask("Tampilkan hanya kandidat terbaik? (y/n) [n]", default="n").lower()

                if view_opt in ("y", "ya", "yes") and best:
                    card = Panel.result(
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
                    Panel.display(card)
                    log_history("Caesar Brute Force", text, best.text, {"best_shift": best.shift})
                    if not _post_result_menu(card, "hasil_caesar_bruteforce.txt"):
                        break
                else:
                    print("\n" + Rule.heavy())
                    print("  TABEL 26 KANDIDAT CAESAR BRUTE FORCE")
                    print(Rule.heavy())
                    print("  Shift | Skor Huruf | Flag | Teks Hasil Dekripsi")
                    print("  ------+------------+------+----------------------------------------")
                    for c in candidates:
                        is_best = best and c.shift == best.shift
                        tag = "  <-- (Kemungkinan Terbesar)" if is_best else ""
                        flag_m = "FLAG" if c.flag_detected else "    "
                        print(f"   [{c.shift:02d}]  |   {c.common_ratio*100:5.1f}%   | {flag_m} | {c.text}{tag}")
                    print(Rule.heavy())
                    if best:
                        Message.success(f"Kandidat Terbaik: Shift {best.shift:02d} -> {best.text}")
                        log_history("Caesar Brute Force", text, best.text, {"best_shift": best.shift})
                    if not _post_result_menu(best.text if best else "", "hasil_caesar_bruteforce.txt"):
                        break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def handle_vigenere() -> None:
    """Interactive handler for Vigenere Cipher."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - VIGENERE CIPHER")
        print(Rule.heavy())
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
            text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
            if not text:
                Message.warning("Teks tidak boleh kosong")
                continue

            key = Prompt.ask("Masukkan kata kunci (huruf alfabet A-Z)")
            if not key:
                Message.warning("Kunci tidak boleh kosong")
                continue
            if not all(c.isalpha() for c in key):
                Message.error("Kunci hanya boleh berisi huruf alfabet tanpa angka atau simbol")
                continue

            if choice == 0:
                out = vigenere_encrypt(text, key)
                card = Panel.result(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Vigenere Cipher",
                    operation="Enkripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=out,
                    extra_fields={"Panjang Kunci": str(len(key))},
                )
                log_history("Vigenere Encrypt", text, out, {"key_length": len(key)})
            else:
                out = vigenere_decrypt(text, key)
                card = Panel.result(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Vigenere Cipher",
                    operation="Dekripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=out,
                    extra_fields={"Panjang Kunci": str(len(key))},
                )
                log_history("Vigenere Decrypt", text, out, {"key_length": len(key)})

            Panel.display(card)
            if not _post_result_menu(card, "hasil_vigenere.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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
            text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
            if not text:
                Message.warning("Teks tidak boleh kosong")
                continue

            key = Prompt.ask("Masukkan kata kunci (huruf alfabet A-Z)")
            if not key:
                Message.warning("Kunci tidak boleh kosong")
                continue
            if not all(c.isalpha() for c in key):
                Message.error("Kunci hanya boleh berisi huruf alfabet tanpa angka atau simbol")
                continue

            if sel == 0:
                res = playfair_encrypt(text, key)
                card = Panel.result(
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
                card = Panel.result(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Playfair Cipher",
                    operation="Dekripsi",
                    status="Berhasil (OK)",
                    input_text=text,
                    output_text=res.output_text,
                    extra_fields={"Key": key, "Note": "Mungkin mengandung padding X"},
                )
                log_history("Playfair Decrypt", text, res.output_text, {"key": key})

            Panel.display(card)
            if not _post_result_menu(card, "hasil_playfair.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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
            text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
            if not text:
                Message.warning("Teks tidak boleh kosong")
                continue

            key = Prompt.ask(f"Masukkan key matrix {size}x{size} (angka 0-25, spasi pemisah)")
            if not key:
                Message.warning("Key matrix tidak boleh kosong")
                continue

            try:
                if sel == 0:
                    res = hill_encrypt(text, key, size)
                    card = Panel.result(
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
                    card = Panel.result(
                        title=f"HASIL OPERASI CRYPTOLAB - HILL {size}x{size}",
                        method="Hill Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Key Matrix": key, "Size": f"{size}x{size}", "Note": "Mungkin mengandung padding X"},
                    )
                    log_history(f"Hill {size}x{size} Decrypt", text, res.output_text, {"key": key, "size": size})

                Panel.display(card)
                if not _post_result_menu(card, f"hasil_hill_{size}x{size}.txt"):
                    break

            except CryptoLabError as err:
                Message.error("Kesalahan Hill", str(err))
            except Exception as err:
                Message.error("Kesalahan tak terduga", str(err))

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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
                text = Prompt.ask("Masukkan ciphertext")
                if not text:
                    Message.warning("Ciphertext tidak boleh kosong")
                    continue

                candidates = affine_brute_force(text)
                if not candidates:
                    Message.warning("Tidak ada kandidat valid")
                    continue

                best = candidates[0]
                card = Panel.result(
                    title="HASIL AFFINE BRUTE FORCE",
                    method=f"Affine (Best: a={best.a}, b={best.b})",
                    operation="Brute Force",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=best.output_text,
                    extra_fields={"Total Candidates": len(candidates), "Top a": best.a, "Top b": best.b},
                )
                Panel.display(card)
                log_history("Affine Brute Force", text, best.output_text, {"candidates": len(candidates)})
                if not _post_result_menu(card, "hasil_affine_brute.txt"):
                    break
                continue

            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
            if not text:
                Message.warning("Teks tidak boleh kosong")
                continue

            a = Prompt.ask_int("Masukkan a (coprime dengan 26: 1,3,5,7,9,11,15,17,19,21,23,25)", min_val=1, max_val=25)
            if a is None:
                continue

            b = Prompt.ask_int("Masukkan b (0-25)", min_val=0, max_val=25)
            if b is None:
                continue

            try:
                if sel == 0:
                    res = affine_encrypt(text, a, b)
                    card = Panel.result(
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
                    card = Panel.result(
                        title="HASIL OPERASI CRYPTOLAB - AFFINE",
                        method="Affine Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"a": str(a), "b": str(b), "a_inv": str(res.a_inv)},
                    )
                    log_history("Affine Decrypt", text, res.output_text, {"a": a, "b": b})

                Panel.display(card)
                if not _post_result_menu(card, "hasil_affine.txt"):
                    break

            except CryptoLabError as err:
                Message.error("Kesalahan", str(err))
            except Exception as err:
                Message.error("Kesalahan tak terduga", str(err))

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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
                text = Prompt.ask("Masukkan ciphertext")
                if not text:
                    Message.warning("Ciphertext tidak boleh kosong")
                    continue

                max_rails = Prompt.ask_int("Maksimal rail [10]", default=10, min_val=2, max_val=20)
                if max_rails is None:
                    continue

                candidates = railfence_brute_force(text, max_rails)
                if not candidates:
                    Message.warning("Tidak ada kandidat valid")
                    continue

                best = candidates[0]
                card = Panel.result(
                    title="HASIL RAIL FENCE BRUTE FORCE",
                    method=f"Rail Fence (Best: {best.rails} rails)",
                    operation="Brute Force",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=best.output_text,
                    extra_fields={"Total Candidates": len(candidates), "Top Rails": best.rails},
                )
                Panel.display(card)
                log_history("Rail Fence Brute Force", text, best.output_text, {"candidates": len(candidates)})
                if not _post_result_menu(card, "hasil_railfence_brute.txt"):
                    break
                continue

            rails = Prompt.ask_int("Jumlah rail (minimal 2)", min_val=2)
            if rails is None:
                continue

            op_name = "Enkripsi" if sel == 0 else "Dekripsi"
            text = Prompt.ask(f"Masukkan teks untuk {op_name.lower()}")
            if not text:
                Message.warning("Teks tidak boleh kosong")
                continue

            try:
                if sel == 0:
                    res = railfence_encrypt(text, rails)
                    pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                    card = Panel.result(
                        title=f"HASIL OPERASI CRYPTOLAB - RAIL FENCE {rails} RAILS",
                        method="Rail Fence Cipher",
                        operation="Enkripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Rails": str(rails)},
                    )
                    Panel.display(card)
                    print(f"\n  Rail Pattern:\n{pattern_str}\n")
                    log_history(f"Rail Fence {rails} Encrypt", text, res.output_text, {"rails": rails})
                else:
                    res = railfence_decrypt(text, rails)
                    pattern_str = "\n".join(f"  Rail {i}: {' '.join(row)}" for i, row in enumerate(res.rail_pattern))
                    card = Panel.result(
                        title=f"HASIL OPERASI CRYPTOLAB - RAIL FENCE {rails} RAILS",
                        method="Rail Fence Cipher",
                        operation="Dekripsi",
                        status="Berhasil (OK)",
                        input_text=text,
                        output_text=res.output_text,
                        extra_fields={"Rails": str(rails)},
                    )
                    Panel.display(card)
                    print(f"\n  Rail Pattern:\n{pattern_str}\n")
                    log_history(f"Rail Fence {rails} Decrypt", text, res.output_text, {"rails": rails})

                if not _post_result_menu(card, f"hasil_railfence_{rails}.txt"):
                    break

            except CryptoLabError as err:
                Message.error("Kesalahan", str(err))
            except Exception as err:
                Message.error("Kesalahan tak terduga", str(err))

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _post_result_menu(result_text: str, default_filename: str = "hasil_cryptolab.txt") -> bool:
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
            _save_result_prompt(result_text, default_filename)


def _save_result_prompt(content: str, default_filename: str = "hasil_cryptolab.txt") -> None:
    """Prompt user to optionally save text content to a file."""
    try:
        choice = Prompt.ask("Simpan hasil ke file? (y/n) [n]", default="n").lower()
        if choice in ("y", "ya", "yes"):
            fn_input = Prompt.ask(f"Nama file [{default_filename}]", default=default_filename)
            filename = fn_input or default_filename
            from pathlib import Path
            filepath = Path(filename)
            filepath.write_text(content, encoding="utf-8")
            Message.success("Hasil berhasil disimpan", str(filepath.resolve()))
    except Exception as err:
        Message.error("Gagal menyimpan file", str(err))
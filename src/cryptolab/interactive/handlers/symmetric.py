"""Symmetric cipher interactive handlers (DES, AES, RC2)."""

import sys
from typing import List, Optional

from cryptolab.symmetric.des import des_encrypt, des_decrypt, des_auto_analyze, DesResult
from cryptolab.symmetric.aes import aes_encrypt, aes_decrypt, aes_auto_analyze, AesResult
from cryptolab.symmetric.rc2 import rc2_encrypt, rc2_decrypt, rc2_auto_analyze, Rc2Result
from cryptolab.banner import warn_ecb_mode, warn_rc2, print_warning

from cryptolab.exceptions import CryptoLabError, InvalidKeyError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, Menu, navigation_menu,
    BackToMenu,
)


def _norm_mode(mode: str) -> str:
    return mode.upper()


def _norm_padding(padding: str) -> str:
    return "PKCS7" if padding.upper() == "PKCS7" else "None"


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
            Message.error("Kesalahan DES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _handle_des_decrypt() -> None:
    """Handle DES decryption with mode selection."""
    while True:
        print("\n" + Rule.heavy())
        print("  DES DEKRIPSI - Pilih Mode")
        print(Rule.heavy())

        mode_sel = navigation_menu(
            options=[
                "Auto (analisis heuristik mode dan padding, key & IV opsional)",
                "CBC (Cipher Block Chaining - membutuhkan IV 8 byte)",
                "ECB (Electronic Codebook - tanpa IV) ⚠️",
            ],
            title="DES DEKRIPSI - Pilih Mode",
            back_label="Kembali ke Menu DES",
        )

        if mode_sel is None:
            break

        try:
            ct_hex = Prompt.ask("Masukkan ciphertext (format heksadesimal)")
            if not ct_hex:
                Message.warning("Ciphertext heksadesimal tidak boleh kosong")
                continue

            # Warning for ECB mode
            if mode_sel == 2:
                print_warning(warn_ecb_mode())

            if mode_sel == 0:
                # Auto mode - key and IV are optional
                print("\n  Mode Auto: Key dan IV opsional (tekan Enter untuk melewati)")
                key = Prompt.ask("Masukkan key (tepat 8 karakter/byte, Enter untuk skip)", allow_empty=True)
                key_val = key if len(key.encode("utf-8")) == 8 else None

                iv = None
                if key_val:
                    iv_cand = Prompt.ask("Masukkan IV (8 karakter untuk CBC, Enter untuk skip/ECB)", allow_empty=True)
                    iv = iv_cand if len(iv_cand.encode("utf-8")) == 8 else None

                if key_val is None:
                    Message.warning("Key dilewati. Auto analisis memerlukan key. Gunakan mode CBC/ECB manual.")
                    continue

                candidates: List[DesResult] = des_auto_analyze(ct_hex, key=key_val, iv=iv)

                if not candidates:
                    Message.warning("Tidak ada konfigurasi DES yang berhasil secara teknis")
                    continue

                top = candidates[0]
                card = Panel.result(
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
                Panel.display(card)

                if len(candidates) > 1:
                    print("\n  KANDIDAT MODE/PADDING LAIN:")
                    print("  " + Rule.light())
                    for idx, c in enumerate(candidates[1:], start=1):
                        prev = c.output_text[:35] + ("..." if len(c.output_text) > 35 else "")
                        print(f"  [{idx}] Mode {c.mode} | Padding {c.padding} | Skor: {c.score:.1f}/100 -> {prev}")

                print(Rule.thin())
                print("  Catatan: Ciphertext heksadesimal tidak membuktikan mode CBC atau ECB.")
                print("  Hasil ditampilkan sebagai kandidat heuristik terverifikasi.")
                print(Rule.heavy())

                log_history("DES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                if not _post_result_menu(card, "hasil_des.txt"):
                    break

            else:
                mode = "CBC" if mode_sel == 1 else "ECB"
                key = Prompt.ask("Masukkan key (tepat 8 karakter/byte)")
                if len(key.encode("utf-8")) != 8:
                    Message.error(f"Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)")
                    continue

                iv: Optional[str] = None
                if mode == "CBC":
                    iv = Prompt.ask("Masukkan IV (tepat 8 karakter/byte)")
                    if len(iv.encode("utf-8")) != 8:
                        Message.error(f"Panjang IV DES CBC harus tepat 8 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)")
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

                card = Panel.result(
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
                Panel.display(card)

                log_history("DES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                if not _post_result_menu(card, "hasil_des.txt"):
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan DES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _handle_des_encrypt() -> None:
    """Handle DES encryption."""
    while True:
        plaintext = Prompt.ask("Masukkan plaintext untuk dienkripsi")
        if not plaintext:
            Message.warning("Plaintext tidak boleh kosong")
            continue

        mode_sel = navigation_menu(
            options=[
                "CBC (Cipher Block Chaining - membutuhkan IV 8 byte) [Default]",
                "ECB (Electronic Codebook - tanpa IV) ⚠️",
            ],
            title="DES ENKRIPSI - Pilih Mode",
            back_label="Batal",
        )
        if mode_sel is None:
            break

        mode = "CBC" if mode_sel == 0 else "ECB"

        # Warning for ECB mode
        if mode == "ECB":
            print_warning(warn_ecb_mode())

        key = Prompt.ask("Masukkan key (tepat 8 karakter/byte)")
        if len(key.encode("utf-8")) != 8:
            Message.error(f"Panjang key DES harus tepat 8 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)")
            continue

        iv = None
        if mode == "CBC":
            iv = Prompt.ask("Masukkan IV (tepat 8 karakter/byte)")
            if len(iv.encode("utf-8")) != 8:
                Message.error(f"Panjang IV DES CBC harus tepat 8 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)")
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

        card = Panel.result(
            title="HASIL OPERASI CRYPTOLAB - DES ENCRYPT",
            method=f"DES ({mode})",
            operation="Enkripsi",
            status="Berhasil (OK)",
            input_text=plaintext,
            output_text=res_enc.output_text,
            reasons=["Enkripsi selesai tanpa kesalahan"],
            extra_fields={"Mode": mode, "Padding": padding},
        )
        Panel.display(card)

        log_history("DES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

        if not _post_result_menu(card, "hasil_des_encrypt.txt"):
            break


def _handle_des_auto_analyze() -> None:
    """Handle DES auto analyze."""
    while True:
        print("\n" + Rule.heavy())
        print("  DES AUTO ANALISIS")
        print(Rule.heavy())
        print("  Fitur ini menguji kombinasi mode (CBC/ECB) dan padding (PKCS7/None)")
        print("  Key diperlukan, IV opsional (tekan Enter untuk melewati).")
        print(Rule.thin())

        try:
            ct_hex = Prompt.ask("Masukkan ciphertext heksadesimal")
            if not ct_hex:
                Message.warning("Ciphertext tidak boleh kosong")
                continue

            key = Prompt.ask("Masukkan key (tepat 8 karakter/byte, Enter untuk skip)", allow_empty=True)
            key_val = key if len(key.encode("utf-8")) == 8 else None

            iv_val: Optional[str] = None
            if key_val:
                iv_cand = Prompt.ask("Masukkan IV (8 karakter untuk CBC, Enter untuk skip)", allow_empty=True)
                iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 8 else None

            if key_val is None:
                Message.warning("Key dilewati. DES tidak dapat didekripsi tanpa key.")
                continue

            candidates = des_auto_analyze(ct_hex, key=key_val, iv=iv_val)

            if candidates:
                top = candidates[0]
                card = Panel.result(
                    title="HASIL ANALISIS DES",
                    method=f"DES ({top.mode}, Padding {top.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={"Mode": top.mode, "Padding": top.padding},
                )
                Panel.display(card)
                log_history("DES Auto Analyze", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})
                if not _post_result_menu(card, "hasil_des_auto.txt"):
                    break
            else:
                Message.warning("Tidak ada kombinasi DES yang valid dengan parameter tersebut")

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan DES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def handle_aes() -> None:
    """Interactive handler for AES (Advanced Encryption Standard - 128 bit CBC/ECB)."""
    while True:
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
                _handle_aes_decrypt()
            elif sel == 1:
                _handle_aes_encrypt()
            elif sel == 2:
                _handle_aes_auto_analyze()

        except BackToMenu:
            continue
        except CryptoLabError as err:
            Message.error("Kesalahan AES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _handle_aes_decrypt() -> None:
    """Handle AES decryption with mode selection."""
    while True:
        print("\n" + Rule.heavy())
        print("  AES DEKRIPSI - Pilih Mode")
        print(Rule.heavy())

        mode_sel = navigation_menu(
            options=[
                "Auto (analisis heuristik mode dan padding yang valid, key & IV opsional)",
                "CBC (Cipher Block Chaining - membutuhkan IV 16 byte)",
                "ECB (Electronic Codebook - tanpa IV) ⚠️",
            ],
            title="AES DEKRIPSI - Pilih Mode",
            back_label="Kembali ke Menu AES",
        )

        if mode_sel is None:
            break

        try:
            ct_hex = Prompt.ask("Masukkan ciphertext (format heksadesimal)")
            if not ct_hex:
                Message.warning("Ciphertext heksadesimal tidak boleh kosong")
                continue

            # Warning for ECB mode
            if mode_sel == 2:
                print_warning(warn_ecb_mode())

            if mode_sel == 0:
                # Auto mode - key and IV are optional
                print("\n  Mode Auto: Key dan IV opsional (tekan Enter untuk melewati)")
                key = Prompt.ask("Masukkan key (tepat 16 karakter/byte, Enter untuk skip)", allow_empty=True)
                key_val = key if len(key.encode("utf-8")) == 16 else None

                iv_val: Optional[str] = None
                if key_val:
                    iv_cand = Prompt.ask("Masukkan IV (16 karakter untuk CBC, Enter untuk skip)", allow_empty=True)
                    iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 16 else None

                if key_val is None:
                    Message.warning("Key dilewati. AES tidak dapat didekripsi tanpa key.")
                    continue

                candidates = aes_auto_analyze(ct_hex, key=key_val, iv=iv_val)

                if candidates:
                    top = candidates[0]
                    card = Panel.result(
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
                    Panel.display(card)

                    if len(candidates) > 1:
                        print("\n  KANDIDAT MODE/PADDING LAIN:")
                        print("  " + Rule.light())
                        for idx, c in enumerate(candidates[1:], start=1):
                            prev = c.output_text[:35] + ("..." if len(c.output_text) > 35 else "")
                            print(f"  [{idx}] Mode {c.mode} | Padding {c.padding} | Skor: {c.score:.1f}/100 -> {prev}")

                    print(Rule.thin())
                    print("  Catatan: Ciphertext heksadesimal tidak membuktikan mode CBC atau ECB.")
                    print("  Hasil ditampilkan sebagai kandidat heuristik terverifikasi.")
                    print(Rule.heavy())

                    log_history("AES Auto Decrypt", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})

                    if not _post_result_menu(card, "hasil_aes.txt"):
                        break
                else:
                    Message.warning("Tidak ada konfigurasi AES yang berhasil didekripsi")

            else:
                mode = "CBC" if mode_sel == 1 else "ECB"
                key = Prompt.ask("Masukkan key (tepat 16 karakter/byte)")
                if len(key.encode("utf-8")) != 16:
                    Message.error(f"Panjang key AES harus tepat 16 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)")
                    continue

                iv: Optional[str] = None
                if mode == "CBC":
                    iv = Prompt.ask("Masukkan IV (tepat 16 karakter/byte)")
                    if len(iv.encode("utf-8")) != 16:
                        Message.error(f"Panjang IV AES CBC harus tepat 16 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)")
                        continue

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

                card = Panel.result(
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
                Panel.display(card)

                log_history("AES Decrypt", ct_hex, res.output_text, {"mode": mode, "padding": padding})

                if not _post_result_menu(card, "hasil_aes.txt"):
                    break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan AES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def _handle_aes_encrypt() -> None:
    """Handle AES encryption."""
    while True:
        plaintext = Prompt.ask("Masukkan plaintext untuk dienkripsi")
        if not plaintext:
            Message.warning("Plaintext tidak boleh kosong")
            continue

        mode_sel = navigation_menu(
            options=[
                "CBC (Cipher Block Chaining - membutuhkan IV 16 byte) [Default]",
                "ECB (Electronic Codebook - tanpa IV) ⚠️",
            ],
            title="AES ENKRIPSI - Pilih Mode",
            back_label="Batal",
        )
        if mode_sel is None:
            break

        mode = "CBC" if mode_sel == 0 else "ECB"

        # Warning for ECB mode
        if mode == "ECB":
            print_warning(warn_ecb_mode())

        key = Prompt.ask("Masukkan key (tepat 16 karakter/byte)")
        if len(key.encode("utf-8")) != 16:
            Message.error(f"Panjang key AES-128 harus tepat 16 byte. (Ditemukan: {len(key.encode('utf-8'))} byte)")
            continue

        iv = None
        if mode == "CBC":
            iv = Prompt.ask("Masukkan IV (tepat 16 karakter/byte)")
            if len(iv.encode("utf-8")) != 16:
                Message.error(f"Panjang IV AES CBC harus tepat 16 byte. (Ditemukan: {len(iv.encode('utf-8'))} byte)")
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

        card = Panel.result(
            title="HASIL OPERASI CRYPTOLAB - AES ENCRYPT",
            method=f"AES-128 ({mode})",
            operation="Enkripsi",
            status="Berhasil (OK)",
            input_text=plaintext,
            output_text=res_enc.output_text,
            reasons=["Enkripsi selesai tanpa kesalahan"],
            extra_fields={"Mode": mode, "Padding": padding},
        )
        Panel.display(card)

        log_history("AES Encrypt", plaintext, res_enc.output_text, {"mode": mode, "padding": padding})

        if not _post_result_menu(card, "hasil_aes_encrypt.txt"):
            break


def _handle_aes_auto_analyze() -> None:
    """Handle AES auto analyze."""
    while True:
        print("\n" + Rule.heavy())
        print("  AES AUTO ANALISIS")
        print(Rule.heavy())
        print("  Fitur ini menguji kombinasi mode (CBC/ECB) dan padding (PKCS7/None)")
        print("  Key diperlukan, IV opsional (tekan Enter untuk melewati).")
        print(Rule.thin())

        try:
            ct_hex = Prompt.ask("Masukkan ciphertext heksadesimal")
            if not ct_hex:
                Message.warning("Ciphertext tidak boleh kosong")
                continue

            key = Prompt.ask("Masukkan key (tepat 16 karakter/byte, Enter untuk skip)", allow_empty=True)
            key_val = key if len(key.encode("utf-8")) == 16 else None

            iv_val: Optional[str] = None
            if key_val:
                iv_cand = Prompt.ask("Masukkan IV (16 karakter untuk CBC, Enter untuk skip)", allow_empty=True)
                iv_val = iv_cand if len(iv_cand.encode("utf-8")) == 16 else None

            if key_val is None:
                Message.warning("Key dilewati. AES tidak dapat didekripsi tanpa key.")
                continue

            candidates = aes_auto_analyze(ct_hex, key=key_val, iv=iv_val)

            if candidates:
                top = candidates[0]
                card = Panel.result(
                    title="HASIL ANALISIS AES",
                    method=f"AES-128 ({top.mode}, Padding {top.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=ct_hex,
                    output_text=top.output_text if top.is_utf8 else f"[Bytes Hex] {top.output_text}",
                    reasons=top.reasons,
                    extra_fields={"Mode": top.mode, "Padding": top.padding},
                )
                Panel.display(card)
                log_history("AES Auto Analyze", ct_hex, top.output_text, {"mode": top.mode, "padding": top.padding})
                if not _post_result_menu(card, "hasil_aes_auto.txt"):
                    break
            else:
                Message.warning("Tidak ada kombinasi AES yang valid dengan parameter tersebut")

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan AES", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def handle_rc2() -> None:
    """Interactive handler for legacy RC2/ARC2 (CBC/ECB)."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - RC2 (ARC2) LEGACY 64-BIT")
        print(Rule.heavy())
        print("  RC2 hanya untuk praktikum, CTF, dan kompatibilitas data lama.")
        print("  Default effective key length: 128 bit.")
        print_warning(warn_rc2())
        print(Rule.thin())
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
                text = Prompt.ask("Masukkan ciphertext heksadesimal")
            elif choice == 1:
                text = Prompt.ask("Masukkan plaintext")
            else:
                text = Prompt.ask("Masukkan ciphertext heksadesimal")
            if not text:
                Message.warning("Input tidak boleh kosong")
                continue

            key = Prompt.ask("Masukkan key RC2 (5-16 byte)")
            if not 5 <= len(key.encode("utf-8")) <= 16:
                Message.error(f"Panjang key RC2 harus 5-16 byte. Ditemukan: {len(key.encode('utf-8'))} byte")
                continue

            iv: Optional[str] = None
            if choice == 2:
                iv_input = Prompt.ask("Masukkan IV CBC (8 byte), atau Enter untuk ECB", allow_empty=True)
                if iv_input:
                    if len(iv_input.encode("utf-8")) != 8:
                        Message.error("Panjang IV RC2 CBC harus tepat 8 byte")
                        continue
                    iv = iv_input
                candidates = rc2_auto_analyze(text, key=key, iv=iv)
                if not candidates:
                    Message.warning("Tidak ada konfigurasi RC2 yang berhasil")
                    continue
                result = candidates[0]
                card = Panel.result(
                    title="HASIL ANALISIS RC2",
                    method=f"RC2 ({result.mode}, Padding {result.padding})",
                    operation="Auto Analisis",
                    status="Kandidat ditemukan",
                    input_text=text,
                    output_text=result.output_text if result.is_utf8 else f"[Bytes Hex] {result.output_text}",
                    reasons=result.reasons,
                    extra_fields={"Mode": result.mode, "Padding": result.padding, "Effective Key Length": "128 bit"},
                )
                Panel.display(card)
                log_history("RC2 Auto Analyze", text, result.output_text, {"mode": result.mode, "padding": result.padding})
                if not _post_result_menu(card, "hasil_rc2_auto.txt"):
                    break
                continue

            mode_sel = navigation_menu(
                options=[
                    "CBC (Cipher Block Chaining - membutuhkan IV 8 byte)",
                    "ECB (Electronic Codebook - tanpa IV) ⚠️",
                ],
                title="RC2 - Pilih Mode",
                back_label="Batal",
            )
            if mode_sel is None:
                continue
            mode = "CBC" if mode_sel == 0 else "ECB"

            # Warning for ECB mode
            if mode == "ECB":
                print_warning(warn_ecb_mode())

            if mode == "CBC":
                iv = Prompt.ask("Masukkan IV (tepat 8 karakter/byte)")
                if len(iv.encode("utf-8")) != 8:
                    Message.error("Panjang IV RC2 CBC harus tepat 8 byte")
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
            card = Panel.result(
                title=title,
                method=f"RC2 ({mode})",
                operation=operation,
                status="Berhasil (OK)",
                input_text=text,
                output_text=output,
                reasons=result.reasons,
                extra_fields={"Mode": mode, "Padding": padding, "Effective Key Length": "128 bit"},
            )
            Panel.display(card)
            log_history(history_operation, text, output, {"mode": mode, "padding": padding})
            if not _post_result_menu(card, "hasil_rc2.txt"):
                break
        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan RC2", str(err))
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
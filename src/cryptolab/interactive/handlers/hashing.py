"""Hashing & password interactive handlers (Hash, HMAC, PBKDF2, Bcrypt, Random)."""

import sys
from typing import Optional

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
    BCRYPT_AVAILABLE,
)
from cryptolab.banner import warn_weak_hash, print_warning

from cryptolab.exceptions import CryptoLabError, InvalidInputError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, navigation_menu,
    BackToMenu,
)


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
            Message.error("Kesalahan Hashing", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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

        # Show warning for weak hash algorithms
        warning = warn_weak_hash(algo)
        if warning:
            print_warning(warning)

        enc_sel = navigation_menu(
            options=["Hexadecimal", "Base64"],
            title=f"{algo} - Pilih Format Output",
            back_label="Kembali",
        )
        if enc_sel is None:
            continue
        encoding = "hex" if enc_sel == 0 else "base64"

        data = Prompt.ask(f"Masukkan data untuk {algo} hash")
        if not data:
            Message.warning("Data tidak boleh kosong")
            continue

        res = hash_compute(data, algorithm=algo, encoding=encoding)
        card = Panel.result(
            title=f"HASIL HASH {algo}",
            method=f"{algo} Hash",
            operation="COMPUTE",
            status="Berhasil (OK)",
            input_text=data,
            output_text=res.output_hash,
            reasons=[f"Output dalam format {encoding.upper()}"],
            extra_fields={"Algorithm": algo, "Encoding": encoding.upper()},
        )
        Panel.display(card)
        log_history(f"Hash {algo} Compute", data, res.output_hash, {"algo": algo, "encoding": encoding})
        if not _post_result_menu(card, f"hasil_hash_{algo.lower()}.txt"):
            break


def _handle_hash_file() -> None:
    """Handle file hashing."""
    while True:
        filepath = Prompt.ask("Masukkan path file")
        if not filepath:
            Message.warning("Path file tidak boleh kosong")
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
            card = Panel.result(
                title=f"HASIL HASH FILE {algo}",
                method=f"{algo} Hash",
                operation="FILE",
                status="Berhasil (OK)",
                input_text=filepath,
                output_text=res.output_hash,
                reasons=["File dibaca dalam chunk 8KB"],
                extra_fields={"Algorithm": algo, "File": filepath},
            )
            Panel.display(card)
            log_history(f"Hash {algo} File", filepath, res.output_hash, {"algo": algo, "filepath": filepath})
            if not _post_result_menu(card, f"hasil_hash_file_{algo.lower()}.txt"):
                break
        except InvalidInputError as e:
            Message.error("Kesalahan", str(e))
        except Exception as e:
            Message.error("Gagal membaca file", str(e))


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

        data = Prompt.ask("Masukkan data asli")
        if not data:
            Message.warning("Data tidak boleh kosong")
            continue

        expected = Prompt.ask("Masukkan hash yang diharapkan")
        if not expected:
            Message.warning("Hash yang diharapkan tidak boleh kosong")
            continue

        res = hash_verify_integrity(data, expected, algorithm=algo, encoding=encoding)
        status = "VALID (COCOK)" if res.match else "INVALID (TIDAK COCOK)"
        card = Panel.result(
            title=f"VERIFIKASI INTEGRITAS {algo}",
            method=f"{algo} Verify",
            operation="VERIFY",
            status=status,
            input_text=data,
            output_text="COCOK" if res.match else "TIDAK COCOK",
            reasons=res.reasons,
            extra_fields={"Algorithm": algo, "Expected": expected, "Status": "VALID" if res.match else "INVALID"},
        )
        Panel.display(card)
        log_history(f"Hash {algo} Verify", data, "COCOK" if res.match else "TIDAK COCOK", {"algo": algo, "match": res.match})
        if not _post_result_menu(card, f"hasil_hash_verify_{algo.lower()}.txt"):
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
            message = Prompt.ask("Masukkan pesan")
            if not message:
                Message.warning("Pesan tidak boleh kosong")
                continue
            key = Prompt.ask("Masukkan kunci rahasia")
            if not key:
                Message.warning("Kunci tidak boleh kosong")
                continue

            res = hmac_compute(message, key, algorithm=algo, encoding=encoding)
            card = Panel.result(
                title=f"HASIL HMAC-{algo}",
                method=f"HMAC-{algo}",
                operation="COMPUTE",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_hmac,
                reasons=[f"Key length: {len(key)} bytes", f"Output: {encoding.upper()}"],
                extra_fields={"Algorithm": f"HMAC-{algo}", "Encoding": encoding.upper()},
            )
            Panel.display(card)
            log_history(f"HMAC-{algo} Compute", message, res.output_hmac, {"algo": algo, "encoding": encoding})
            if not _post_result_menu(card, f"hasil_hmac_{algo.lower()}.txt"):
                break

        else:
            # Verify
            message = Prompt.ask("Masukkan pesan")
            if not message:
                Message.warning("Pesan tidak boleh kosong")
                continue
            key = Prompt.ask("Masukkan kunci rahasia")
            if not key:
                Message.warning("Kunci tidak boleh kosong")
                continue
            expected = Prompt.ask("Masukkan HMAC yang diharapkan")
            if not expected:
                Message.warning("HMAC yang diharapkan tidak boleh kosong")
                continue

            match = hmac_verify(message, key, expected, algorithm=algo, encoding=encoding)
            status = "VALID (COCOK)" if match else "INVALID (TIDAK COCOK)"
            card = Panel.result(
                title=f"VERIFIKASI HMAC-{algo}",
                method=f"HMAC-{algo}",
                operation="VERIFY",
                status=status,
                input_text=message,
                output_text="COCOK" if match else "TIDAK COCOK",
                reasons=["Konstanta-time comparison"],
                extra_fields={"Algorithm": f"HMAC-{algo}", "Status": "VALID" if match else "INVALID"},
            )
            Panel.display(card)
            log_history(f"HMAC-{algo} Verify", message, "COCOK" if match else "TIDAK COCOK", {"algo": algo, "match": match})
            if not _post_result_menu(card, f"hasil_hmac_verify_{algo.lower()}.txt"):
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
            password = Prompt.ask("Masukkan password")
            if not password:
                Message.warning("Password tidak boleh kosong")
                continue

            salt_input = Prompt.ask("Masukkan salt (hex/base64, kosong untuk random)", allow_empty=True)
            salt = salt_input if salt_input else None

            iterations = Prompt.ask_int("Jumlah iterasi [100000]", default=100000, min_val=1000)
            if iterations is None:
                continue

            dklen = Prompt.ask_int("Derived key length (bytes) [32]", default=32, min_val=1, max_val=128)
            if dklen is None:
                continue

            res = pbkdf2_hash(password, salt=salt, iterations=iterations, algorithm=algo, dklen=dklen, encoding=encoding)
            output_text = f"Salt: {res.salt}\nHash: {res.hash_value}"
            card = Panel.result(
                title=f"HASIL PBKDF2-{algo}",
                method=f"PBKDF2-{algo}",
                operation="HASH",
                status="Berhasil (OK)",
                input_text="********",
                output_text=output_text,
                reasons=[f"Salt: {res.salt}", f"DKLen: {dklen} bytes", f"Output: {encoding.upper()}"],
                extra_fields={"Algorithm": f"PBKDF2-{algo}", "Iterations": f"{iterations:,}", "DKLen": f"{dklen} bytes", "Encoding": encoding.upper()},
            )
            Panel.display(card)
            log_history(f"PBKDF2-{algo} Hash", "********", res.hash_value, {"algo": algo, "iterations": iterations, "salt": res.salt})
            if not _post_result_menu(card, f"hasil_pbkdf2_{algo.lower()}.txt"):
                break

        else:
            # Verify
            password = Prompt.ask("Masukkan password")
            if not password:
                Message.warning("Password tidak boleh kosong")
                continue

            salt = Prompt.ask("Masukkan salt (hex/base64)")
            if not salt:
                Message.warning("Salt tidak boleh kosong")
                continue

            expected = Prompt.ask("Masukkan hash yang diharapkan")
            if not expected:
                Message.warning("Hash yang diharapkan tidak boleh kosong")
                continue

            iterations = Prompt.ask_int("Jumlah iterasi [100000]", default=100000)
            if iterations is None:
                continue

            dklen = Prompt.ask_int("Derived key length (bytes) [32]", default=32)
            if dklen is None:
                continue

            res = pbkdf2_verify(password, salt, expected, iterations=iterations, algorithm=algo, dklen=dklen, encoding=encoding)
            status = "COCOK" if res.match else "TIDAK COCOK"
            card = Panel.result(
                title=f"VERIFIKASI PBKDF2-{algo}",
                method=f"PBKDF2-{algo}",
                operation="VERIFY",
                status=status,
                input_text="********",
                output_text=status,
                reasons=res.reasons,
                extra_fields={"Algorithm": f"PBKDF2-{algo}", "Status": status},
            )
            Panel.display(card)
            log_history(f"PBKDF2-{algo} Verify", "********", status, {"algo": algo, "match": res.match})
            if not _post_result_menu(card, f"hasil_pbkdf2_verify_{algo.lower()}.txt"):
                break


def _handle_bcrypt() -> None:
    """Handle Bcrypt operations."""
    if not BCRYPT_AVAILABLE:
        Message.error("Bcrypt", "Bcrypt tidak tersedia (bcrypt package not installed)")
        return

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
            password = Prompt.ask("Masukkan password")
            if not password:
                Message.warning("Password tidak boleh kosong")
                continue

            rounds = Prompt.ask_int("Cost factor/rounds (4-31) [12]", default=12, min_val=4, max_val=31)
            if rounds is None:
                continue

            res = bcrypt_hash(password, rounds=rounds)
            card = Panel.result(
                title="HASIL BCRYPT",
                method="BCRYPT",
                operation="HASH",
                status="Berhasil (OK)",
                input_text="********",
                output_text=res.hash_value,
                reasons=["Adaptive hash dengan salt otomatis", "Cocok untuk penyimpanan password"],
                extra_fields={"Algorithm": "BCRYPT", "Rounds": str(rounds)},
            )
            Panel.display(card)
            log_history("Bcrypt Hash", "********", res.hash_value, {"rounds": rounds})
            if not _post_result_menu(card, "hasil_bcrypt.txt"):
                break

        else:
            # Verify
            password = Prompt.ask("Masukkan password")
            if not password:
                Message.warning("Password tidak boleh kosong")
                continue

            expected = Prompt.ask("Masukkan hash bcrypt")
            if not expected:
                Message.warning("Hash tidak boleh kosong")
                continue

            res = bcrypt_verify(password, expected)
            status = "COCOK" if res.match else "TIDAK COCOK"
            card = Panel.result(
                title="VERIFIKASI BCRYPT",
                method="BCRYPT",
                operation="VERIFY",
                status=status,
                input_text="********",
                output_text=status,
                reasons=res.reasons,
                extra_fields={"Algorithm": "BCRYPT", "Status": status},
            )
            Panel.display(card)
            log_history("Bcrypt Verify", "********", status, {"match": res.match})
            if not _post_result_menu(card, "hasil_bcrypt_verify.txt"):
                break


def _handle_random_bytes() -> None:
    """Handle random bytes generation."""
    while True:
        length = Prompt.ask_int("Panjang random bytes (1-1024) [32]", default=32, min_val=1, max_val=1024)
        if length is None:
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
        card = Panel.result(
            title="RANDOM BYTES",
            method="CSPRNG",
            operation="GENERATE",
            status="Berhasil (OK)",
            input_text="",
            output_text=out,
            reasons=["Cryptographically secure random (secrets.token_bytes)"],
            extra_fields={"Length": f"{length} bytes", "Encoding": encoding.upper()},
        )
        Panel.display(card)
        log_history("Random Bytes", "", out, {"length": length, "encoding": encoding})
        if not _post_result_menu(card, "hasil_random.txt"):
            break


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
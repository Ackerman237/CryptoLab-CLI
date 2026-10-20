"""Asymmetric interactive handlers (RSA, DH)."""

import sys
from typing import Optional

from cryptolab.asymmetric import (
    rsa_generate_keypair,
    rsa_encrypt,
    rsa_decrypt,
    rsa_sign,
    rsa_verify,
    dh_key_exchange,
    dh_derive_key,
)
from cryptolab.banner import warn_rsa_pkcs1v15, print_warning

from cryptolab.exceptions import CryptoLabError, InvalidInputError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, navigation_menu,
    BackToMenu,
)


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
            Message.error("Kesalahan RSA", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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

        Message.info("Menghasilkan RSA key pair", f"{key_size}-bit...")
        kp = rsa_generate_keypair(key_size)

        print("\n" + Rule.heavy())
        print(f"  RSA {key_size}-BIT KEY PAIR GENERATED")
        print(Rule.heavy())
        print("\n  PRIVATE KEY (Simpan dengan aman!):")
        print("  " + "\n  ".join(kp.private_key_pem.strip().split("\n")))
        print("\n  PUBLIC KEY (Bisa dibagikan):")
        print("  " + "\n  ".join(kp.public_key_pem.strip().split("\n")))
        print(Rule.heavy())

        save_private = Prompt.ask("Simpan private key ke file? (y/n) [n]", default="n").lower()
        if save_private in ("y", "ya", "yes"):
            fname = Prompt.ask("Nama file private key [rsa_private.pem]", default="rsa_private.pem")
            with open(fname, "w") as f:
                f.write(kp.private_key_pem)
            Message.success("Private key disimpan", fname)

        save_public = Prompt.ask("Simpan public key ke file? (y/n) [n]", default="n").lower()
        if save_public in ("y", "ya", "yes"):
            fname = Prompt.ask("Nama file public key [rsa_public.pem]", default="rsa_public.pem")
            with open(fname, "w") as f:
                f.write(kp.public_key_pem)
            Message.success("Public key disimpan", fname)

        log_history(f"RSA KeyGen {key_size}", "", "KEYPAIR GENERATED", {"keysize": key_size})
        if not _post_result_menu("", f"hasil_rsa_keygen_{key_size}.txt"):
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
        filepath = Prompt.ask("Path file key")
        try:
            with open(filepath, "r") as f:
                return f.read().strip()
        except OSError as e:
            Message.error("Gagal membaca file", str(e))
            raise BackToMenu()
    else:
        print("  Paste key (akhiri dengan baris kosong):")
        lines = []
        while True:
            try:
                line = input("  ")
                if not line:
                    break
                lines.append(line)
            except (KeyboardInterrupt, EOFError):
                raise BackToMenu()
        if not lines:
            Message.error("Key", "Key tidak boleh kosong")
            raise BackToMenu()
        return "\n".join(lines)


def _handle_rsa_encrypt() -> None:
    """Handle RSA encryption."""
    while True:
        message = Prompt.ask("Masukkan plaintext untuk dienkripsi")
        if not message:
            Message.print_warning("Plaintext tidak boleh kosong")
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
            card = Panel.result(
                title=f"HASIL RSA ENKRIPSI",
                method=f"RSA-{res.algorithm}",
                operation="ENCRYPT",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_text,
                reasons=[f"Key size: {res.key_size} bit", f"Padding: {padding}", f"Encoding: {encoding.upper()}"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            Panel.display(card)
            log_history(f"RSA Encrypt", message, res.output_text, {"algo": res.algorithm})
            if not _post_result_menu(card, "hasil_rsa_encrypt.txt"):
                break
        except Exception as e:
            Message.error("Enkripsi gagal", str(e))


def _handle_rsa_decrypt() -> None:
    """Handle RSA decryption."""
    while True:
        ciphertext = Prompt.ask("Masukkan ciphertext")
        if not ciphertext:
            Message.print_warning("Ciphertext tidak boleh kosong")
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
            card = Panel.result(
                title=f"HASIL RSA DEKRIPSI",
                method=f"RSA-{res.algorithm}",
                operation="DECRYPT",
                status="Berhasil (OK)" if not res.is_hex else "Berhasil (Output Hex)",
                input_text=f"[{len(ciphertext)} chars ciphertext]",
                output_text=res.output_text,
                reasons=["UTF-8 valid" if not res.is_hex else "Output bukan UTF-8, ditampilkan hex"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            Panel.display(card)
            log_history(f"RSA Decrypt", ciphertext, res.output_text, {"algo": res.algorithm})
            if not _post_result_menu(card, "hasil_rsa_decrypt.txt"):
                break
        except Exception as e:
            Message.error("Dekripsi gagal", str(e))


def _handle_rsa_sign() -> None:
    """Handle RSA signing."""
    while True:
        message = Prompt.ask("Masukkan pesan untuk ditandatangani")
        if not message:
            Message.print_warning("Pesan tidak boleh kosong")
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
            card = Panel.result(
                title=f"HASIL RSA SIGN",
                method=f"RSA-{res.algorithm}",
                operation="SIGN",
                status="Berhasil (OK)",
                input_text=message,
                output_text=res.output_text,
                reasons=[f"Key size: {res.key_size} bit", f"Hash: {hash_algo}", f"Padding: {sig_padding}"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit"},
            )
            Panel.display(card)
            log_history(f"RSA Sign", message, res.output_text, {"algo": res.algorithm})
            if not _post_result_menu(card, "hasil_rsa_sign.txt"):
                break
        except Exception as e:
            Message.error("Signing gagal", str(e))


def _handle_rsa_verify() -> None:
    """Handle RSA signature verification."""
    while True:
        message = Prompt.ask("Masukkan pesan asli")
        if not message:
            Message.print_warning("Pesan tidak boleh kosong")
            continue

        signature = Prompt.ask("Masukkan signature")
        if not signature:
            Message.print_warning("Signature tidak boleh kosong")
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
            card = Panel.result(
                title=f"VERIFIKASI RSA SIGNATURE",
                method=f"RSA-{res.algorithm}",
                operation="VERIFY",
                status=status,
                input_text=message,
                output_text=res.output_text,
                reasons=["Verifikasi berhasil" if "VALID" in res.output_text else "Tanda tangan tidak cocok"],
                extra_fields={"Algorithm": res.algorithm, "Key Size": f"{res.key_size} bit", "Status": status},
            )
            Panel.display(card)
            log_history(f"RSA Verify", message, res.output_text, {"algo": res.algorithm})
            if not _post_result_menu(card, "hasil_rsa_verify.txt"):
                break
        except Exception as e:
            Message.error("Verifikasi gagal", str(e))


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
            Message.error("Kesalahan DH", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


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

        use_custom = Prompt.ask("Gunakan private key custom? (y/n) [n]", default="n").lower()
        alice_priv = None
        bob_priv = None
        if use_custom in ("y", "ya", "yes"):
            alice_hex = Prompt.ask("Alice private key (hex)")
            bob_hex = Prompt.ask("Bob private key (hex)")
            try:
                alice_priv = int(alice_hex, 16) if alice_hex else None
                bob_priv = int(bob_hex, 16) if bob_hex else None
            except ValueError:
                Message.error("Private key", "harus hex valid")
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
        print("\n" + Rule.heavy())
        print(f"  DHKE {bits}-BIT KEY EXCHANGE")
        print(Rule.heavy())
        print(output)
        print(Rule.heavy())

        derive = Prompt.ask("Derive symmetric key dari shared secret? (y/n) [n]", default="n").lower()
        if derive in ("y", "ya", "yes"):
            keylen = Prompt.ask_int("Key length (bytes) [16]", default=16, min_val=1)
            if keylen is None:
                continue
            try:
                derived = dh_derive_key(res.shared_secret_hex, key_length=keylen)
                Message.success(f"Derived Key ({keylen} bytes)", derived)
            except Exception as e:
                Message.error("Gagal derive", str(e))

        log_history(f"DHKE {bits}", "", "EXCHANGE COMPLETE", {"bits": bits})
        if not _post_result_menu("", f"hasil_dh_{bits}.txt"):
            break


def _handle_dh_derive() -> None:
    """Handle DH key derivation."""
    while True:
        shared = Prompt.ask("Masukkan shared secret (hex)")
        if not shared:
            Message.print_warning("Shared secret tidak boleh kosong")
            continue

        keylen = Prompt.ask_int("Key length (bytes) [32]", default=32, min_val=1)
        if keylen is None:
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
            derived = dh_derive_key(shared, key_length=keylen, hash_algo=hash_algo)
            if encoding == "base64":
                import base64
                derived = base64.b64encode(bytes.fromhex(derived)).decode("ascii")
            card = Panel.result(
                title="DHKE KEY DERIVATION",
                method=f"HKDF-{hash_algo}",
                operation="DERIVE",
                status="Berhasil (OK)",
                input_text=f"Shared Secret: {shared[:32]}...",
                output_text=derived,
                reasons=[f"Key length: {keylen} bytes", f"Hash: {hash_algo}"],
                extra_fields={"Key Length": f"{keylen} bytes", "Hash": hash_algo, "Encoding": encoding.upper()},
            )
            Panel.display(card)
            log_history("DHKE Derive", shared, derived, {"keylen": keylen, "hash": hash_algo})
            if not _post_result_menu(card, "hasil_dh_derive.txt"):
                break
        except Exception as e:
            Message.error("Derive gagal", str(e))


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
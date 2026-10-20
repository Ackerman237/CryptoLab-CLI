"""Encoding interactive handlers (Base64, Hex, Binary)."""

from typing import Optional

from cryptolab.encoding.base64_codec import base64_encode, base64_decode
from cryptolab.encoding.hex_codec import hex_encode, hex_decode
from cryptolab.encoding.binary_codec import binary_encode, binary_decode

from cryptolab.exceptions import CryptoLabError
from cryptolab.utils.history import log_history
from cryptolab.ui import (
    Rule, Panel, Message, Prompt, navigation_menu,
    BackToMenu,
)


# ============================================================
# Tahap 1: pemisah Binary & Hex (menu ▲▼ + Enter, item pertama = default)
# ============================================================

# (label, nilai)  -- nilai None = Kustom (input manual)
BIN_DELIMITERS = [
    ("Spasi (default)", " "),
    ("Tanpa pemisah", ""),
    ("Koma", ","),
    ("Strip", "-"),
    ("Kustom...", None),
]
HEX_DELIMITERS = [
    ("Spasi (default)", " "),
    ("Tanpa pemisah", ""),
    ("Titik dua", ":"),
    ("Strip", "-"),
    ("Prefix 0x", "0x"),
    ("Kustom...", None),
]
def pick_delimiter(options):
    """Pilih pemisah byte via menu navigasi.

    Returns:
        (delimiter, prefix) -- prefix hanya untuk opsi '0x' Hex, selain itu "".
        None bila user membatalkan pilihan (kembali).
    """
    labels = [label for label, _ in options]
    idx = navigation_menu(
        options=labels,
        title="PILIH PEMISAH BYTE",
        back_label="Batal",
    )
    if idx is None:
        return None

    value = options[idx][1]
    if value is None:
        # Kustom: 1-3 karakter simbol saja (tanpa huruf/angka) supaya decode
        # auto-detect tetap bisa membedakan pemisah dari data yang salah ketik.
        while True:
            raw = Prompt.ask(
                "Pemisah kustom (Enter = spasi, maks 3 karakter simbol)",
                allow_empty=True,
                allow_back=False,
            )
            if not raw:
                return (" ", "")
            if len(raw) <= 3 and not raw.isalnum():
                return (raw, "")
            Message.print_warning("Maks 3 karakter dan hanya boleh berupa simbol (tanpa huruf/angka)")
    if value == "0x":
        # Prefix 0x: hex per byte dipisah spasi ("0x48 0x69").
        return (" ", "0x")
    return (value, "")


def handle_base64() -> None:
    """Interactive handler for Base64 codec."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - BASE64 CODEC")
        print(Rule.heavy())
        print("  Catatan: Base64 adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(Rule.thin())
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Base64)", "Decode (Base64 -> Teks UTF-8)"],
            title="CRYPTOLAB - BASE64 CODEC",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            op_name = "Encode" if choice == 0 else "Decode"
            data = Prompt.ask(f"Masukkan data untuk Base64 {op_name.lower()}")
            if not data:
                Message.warning("Data tidak boleh kosong")
                continue

            if choice == 0:
                out = base64_encode(data)
                card = Panel.result(
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
                card = Panel.result(
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

            Panel.display(card)
            if not _post_result_menu(card, "hasil_base64.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def handle_hex() -> None:
    """Interactive handler for Hexadecimal codec."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - HEXADECIMAL CODEC")
        print(Rule.heavy())
        print("  Catatan: Hexadecimal adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(Rule.thin())
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Hex)", "Decode (Hex -> Teks UTF-8)"],
            title="CRYPTOLAB - HEXADECIMAL CODEC",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice == 0:
                data = Prompt.ask("Masukkan teks untuk di-encode ke Hex")
                if not data:
                    Message.warning("Teks tidak boleh kosong")
                    continue

                picked = pick_delimiter(HEX_DELIMITERS)
                if picked is None:
                    continue  # batal pilih pemisah -> kembali ke menu opsi
                delimiter, prefix = picked

                if prefix:
                    pairs = hex_encode(data, delimiter=" ").split(" ")
                    out = delimiter.join(prefix + p for p in pairs)
                else:
                    out = hex_encode(data, delimiter=delimiter)
                extra = {"Kategori": "Encoding", "Pemisah": repr(delimiter)}
                if prefix:
                    extra["Prefix"] = prefix
                card = Panel.result(
                    title="HASIL OPERASI CRYPTOLAB",
                    method="Hexadecimal",
                    operation="Encode",
                    status="Berhasil (OK)",
                    input_text=data,
                    output_text=out,
                    reasons=["Data di-encode ke pasangan byte heksadesimal."],
                    extra_fields=extra,
                )
                log_extra = {"delimiter": delimiter}
                if prefix:
                    log_extra["prefix"] = prefix
                log_history("Hex Encode", data, out, log_extra)
            else:
                data = Prompt.ask("Masukkan string heksadesimal untuk di-decode")
                if not data:
                    Message.warning("Data heksadesimal tidak boleh kosong")
                    continue

                out = hex_decode(data)
                card = Panel.result(
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

            Panel.display(card)
            if not _post_result_menu(card, "hasil_hex.txt"):
                break

        except BackToMenu:
            break
        except CryptoLabError as err:
            Message.error("Kesalahan", str(err))
        except Exception as err:
            Message.error("Kesalahan tak terduga", str(err))


def handle_binary() -> None:
    """Interactive handler for Binary codec."""
    while True:
        print("\n" + Rule.heavy())
        print("  CRYPTOLAB - BINARY CODEC (8-BIT)")
        print(Rule.heavy())
        print("  Catatan: Binary adalah ENCODING (bukan enkripsi kriptografi)")
        print("  dan tidak memerlukan key atau IV.")
        print(Rule.thin())
        choice = navigation_menu(
            options=["Encode (Teks UTF-8 -> Biner 8-Bit)", "Decode (Biner 8-Bit -> Teks UTF-8)"],
            title="CRYPTOLAB - BINARY CODEC (8-BIT)",
            back_label="Kembali ke Menu Utama",
        )
        if choice is None:
            break

        try:
            if choice == 0:
                data = Prompt.ask("Masukkan teks untuk di-encode ke Biner")
                if not data:
                    Message.warning("Teks tidak boleh kosong")
                    continue

                picked = pick_delimiter(BIN_DELIMITERS)
                if picked is None:
                    continue  # batal pilih pemisah -> kembali ke menu opsi
                delimiter, _prefix = picked

                out = binary_encode(data, delimiter=delimiter)
                card = Panel.result(
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
                data = Prompt.ask("Masukkan string biner untuk di-decode")
                if not data:
                    Message.warning("Data biner tidak boleh kosong")
                    continue

                out = binary_decode(data)
                card = Panel.result(
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

            Panel.display(card)
            if not _post_result_menu(card, "hasil_binary.txt"):
                break

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
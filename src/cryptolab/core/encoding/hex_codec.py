"""Hexadecimal encoding and decoding codec."""

import re
from ..exceptions import InvalidInputError, DecodingError


def hex_encode(text: str, delimiter: str = " ", encoding: str = "utf-8") -> str:
    """Encode a text string to Hexadecimal byte representation.

    Args:
        text: Plaintext string (supports ASCII and Unicode).
        delimiter: Separator between hex byte pairs (default: ' ').
        encoding: Character encoding for bytes representation (default: utf-8).

    Returns:
        Hexadecimal string representation of the bytes.

    Raises:
        InvalidInputError: If text is empty or not a string.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    if len(text) == 0:
        raise InvalidInputError("Input teks untuk Hex encode tidak boleh kosong.")

    try:
        raw_bytes = text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as err:
        raise InvalidInputError(f"Gagal mengonversi teks ke byte ({encoding}): {err}")

    hex_pairs = [f"{b:02x}" for b in raw_bytes]
    return delimiter.join(hex_pairs)


def hex_decode(hex_str: str, encoding: str = "utf-8") -> str:
    """Decode a Hexadecimal string back to plaintext.

    Supports continuous hex (e.g. '48656c6c6f'), space-delimited ('48 65 6c 6c 6f'),
    colon-delimited ('48:65:6c:6c:6f'), or '0x' prefixed hex.

    Args:
        hex_str: Hexadecimal string to decode.
        encoding: Expected character encoding for output text (default: utf-8).

    Returns:
        Decoded plaintext string.

    Raises:
        InvalidInputError: If hex_str is empty or not a string.
        DecodingError: If hex_str contains invalid characters, odd length, or invalid UTF-8.
    """
    if hex_str is None or not isinstance(hex_str, str):
        raise InvalidInputError("Input Hexadecimal harus berupa string.")

    cleaned = hex_str.strip()
    if len(cleaned) == 0:
        raise InvalidInputError("Input Hexadecimal tidak boleh kosong.")

    # Remove optional '0x' or '0X' prefix if at the start
    # (perilaku lama: '0x' di tengah string TIDAK didukung - lihat baseline Tahap 0)
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]
    original = cleaned

    # Tahap 1: buang semua simbol & whitespace (pemisah umum maupun kustom).
    # Huruf/angka asing TIDAK dibuang agar input salah seperti "4865ZZ" tetap
    # menghasilkan error (perilaku lama), dan 'x' prefix ganda tetap terdeteksi.
    cleaned = re.sub(r"[\W_]", "", cleaned)

    if len(cleaned) == 0:
        invalid_chars = set(re.findall(r"[^0-9a-fA-F]", original)) - set(" \t\r\n")
        if invalid_chars:
            raise DecodingError(
                f"String Hexadecimal mengandung karakter tidak valid: {', '.join(sorted(invalid_chars))}"
            )
        raise InvalidInputError("Input Hexadecimal tidak boleh kosong.")

    # Validate characters: sisa non-hex hanya boleh 'x'/'X' (prefix di tengah)
    if not re.fullmatch(r"[0-9a-fA-F]+", cleaned):
        # Kasus umum: pengguna menempel output bahasa pemrograman ("0x48 0x69").
        # Perilaku lama tetap dipertahankan (input DITOLAK, lihat baseline
        # Tahap 0), tapi pesannya dibuat ramah dan memberi solusi jelas.
        if re.search(r"0[xX][0-9a-fA-F]", original):
            raise DecodingError(
                "Input memakai prefix '0x' di setiap byte (mis. '0x48 0x69'). "
                "Hapus dulu semua '0x'-nya, atau pilih mode pemisah 'Prefix 0x' "
                "saat menulis keluaran Hex."
            )
        invalid_chars = set(re.findall(r"[^0-9a-fA-F]", cleaned))
        raise DecodingError(
            f"String Hexadecimal mengandung karakter tidak valid: {', '.join(sorted(invalid_chars))}"
        )

    # Must be pairs of 2 hex characters (each byte is 2 hex digits)
    if len(cleaned) % 2 != 0:
        raise DecodingError(
            f"Panjang string Hexadecimal ganjil ({len(cleaned)} karakter). Hex byte harus berpasangan (genap)."
        )

    try:
        raw_bytes = bytes.fromhex(cleaned)
    except ValueError as err:
        raise DecodingError(f"Gagal mengonversi string ke byte hexadecimal: {err}")

    try:
        return raw_bytes.decode(encoding)
    except UnicodeDecodeError as err:
        raise DecodingError(
            f"Hasil dekode Hexadecimal bukan teks berenkode {encoding} yang valid ({err})."
        )

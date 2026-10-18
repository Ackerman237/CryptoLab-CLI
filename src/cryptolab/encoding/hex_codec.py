"""Hexadecimal encoding and decoding codec."""

import re
from cryptolab.exceptions import InvalidInputError, DecodingError


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
    if cleaned.startswith(("0x", "0X")):
        cleaned = cleaned[2:]

    # Remove common separators (spaces, colons, dashes)
    cleaned = re.sub(r"[\s:\-]+", "", cleaned)

    if len(cleaned) == 0:
        raise InvalidInputError("Input Hexadecimal tidak boleh kosong.")

    # Validate characters
    if not re.fullmatch(r"[0-9a-fA-F]+", cleaned):
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

"""8-bit Binary encoding and decoding codec."""

import re
from typing import List
from cryptolab.exceptions import InvalidInputError, DecodingError


def binary_encode(text: str, delimiter: str = " ", encoding: str = "utf-8") -> str:
    """Encode a text string into an 8-bit binary representation per byte.

    Args:
        text: Plaintext string (supports ASCII and Unicode).
        delimiter: Separator between 8-bit byte groups (default: ' ').
        encoding: Character encoding for bytes representation (default: utf-8).

    Returns:
        Binary string formatted as 8 bits per byte.

    Raises:
        InvalidInputError: If text is empty or not a string.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    if len(text) == 0:
        raise InvalidInputError("Input teks untuk Binary encode tidak boleh kosong.")

    try:
        raw_bytes = text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as err:
        raise InvalidInputError(f"Gagal mengonversi teks ke byte ({encoding}): {err}")

    byte_binaries = [f"{b:08b}" for b in raw_bytes]
    return delimiter.join(byte_binaries)


def binary_decode(binary_str: str, encoding: str = "utf-8") -> str:
    """Decode an 8-bit binary string back to plaintext.

    Accepts space-separated 8-bit groups (e.g. '01001000 01101001') or continuous
    binary strings with length multiple of 8 (e.g. '0100100001101001').

    Args:
        binary_str: Binary string containing 0s and 1s.
        encoding: Expected character encoding for output text (default: utf-8).

    Returns:
        Decoded plaintext string.

    Raises:
        InvalidInputError: If binary_str is empty or not a string.
        DecodingError: If binary_str contains non-binary characters, wrong bit length, or invalid UTF-8.
    """
    if binary_str is None or not isinstance(binary_str, str):
        raise InvalidInputError("Input Binary harus berupa string.")

    cleaned = binary_str.strip()
    if len(cleaned) == 0:
        raise InvalidInputError("Input Binary tidak boleh kosong.")

    # Check if input is space-separated or delimiter-separated
    tokens = cleaned.split()
    chunks: List[str] = []

    if len(tokens) > 1:
        # User provided separated chunks
        for idx, token in enumerate(tokens, start=1):
            if not re.fullmatch(r"[01]+", token):
                invalid_chars = set(re.findall(r"[^01]", token))
                raise DecodingError(
                    f"Token ke-{idx} ('{token}') mengandung karakter bukan biner: {', '.join(sorted(invalid_chars))}"
                )
            if len(token) != 8:
                raise DecodingError(
                    f"Token ke-{idx} ('{token}') memiliki panjang {len(token)} bit (harus 8-bit per byte)."
                )
            chunks.append(token)
    else:
        # Single token without spaces
        raw_bin = tokens[0]
        if not re.fullmatch(r"[01]+", raw_bin):
            invalid_chars = set(re.findall(r"[^01]", raw_bin))
            raise DecodingError(
                f"String biner mengandung karakter tidak valid: {', '.join(sorted(invalid_chars))}"
            )
        if len(raw_bin) % 8 != 0:
            raise DecodingError(
                f"Panjang string biner ({len(raw_bin)} bit) bukan kelipatan 8 bit."
            )
        chunks = [raw_bin[i : i + 8] for i in range(0, len(raw_bin), 8)]

    try:
        raw_bytes = bytes(int(chunk, 2) for chunk in chunks)
    except ValueError as err:
        raise DecodingError(f"Gagal mengonversi bit biner ke byte: {err}")

    try:
        return raw_bytes.decode(encoding)
    except UnicodeDecodeError as err:
        raise DecodingError(
            f"Hasil dekode Binary bukan teks berenkode {encoding} yang valid ({err})."
        )

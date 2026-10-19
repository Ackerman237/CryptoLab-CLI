"""Base64 encoding and decoding codec."""

import base64
import binascii
from ..exceptions import InvalidInputError, DecodingError


def base64_encode(text: str, encoding: str = "utf-8") -> str:
    """Encode a text string to Base64 using specified character encoding.

    Args:
        text: Input string (supports ASCII and Unicode).
        encoding: Character encoding for bytes representation (default: utf-8).

    Returns:
        Base64 encoded string.

    Raises:
        InvalidInputError: If text is empty or not a string.
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    if len(text) == 0:
        raise InvalidInputError("Input teks untuk Base64 encode tidak boleh kosong.")

    try:
        raw_bytes = text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as err:
        raise InvalidInputError(f"Gagal mengonversi teks ke byte ({encoding}): {err}")

    encoded_bytes = base64.b64encode(raw_bytes)
    return encoded_bytes.decode("ascii")


def base64_decode(encoded_str: str, encoding: str = "utf-8") -> str:
    """Decode a Base64 string back to plaintext.

    Args:
        encoded_str: Base64 encoded string.
        encoding: Expected character encoding for output text (default: utf-8).

    Returns:
        Decoded plaintext string.

    Raises:
        InvalidInputError: If encoded_str is empty or not a string.
        DecodingError: If encoded_str is not valid Base64 or cannot be decoded to text.
    """
    if encoded_str is None or not isinstance(encoded_str, str):
        raise InvalidInputError("Input Base64 harus berupa string.")

    cleaned_str = encoded_str.strip()
    if len(cleaned_str) == 0:
        raise InvalidInputError("Input teks Base64 tidak boleh kosong.")

    # Base64 strings with padding must have a length multiple of 4
    if len(cleaned_str) % 4 != 0:
        raise DecodingError(
            f"Panjang string Base64 tidak valid ({len(cleaned_str)} karakter, harus kelipatan 4)."
        )

    try:
        decoded_bytes = base64.b64decode(cleaned_str, validate=True)
    except (binascii.Error, ValueError) as err:
        raise DecodingError(f"Data bukan format Base64 yang valid: {err}")

    try:
        return decoded_bytes.decode(encoding)
    except UnicodeDecodeError as err:
        raise DecodingError(
            f"Hasil dekode Base64 bukan teks berenkode {encoding} yang valid ({err})."
        )

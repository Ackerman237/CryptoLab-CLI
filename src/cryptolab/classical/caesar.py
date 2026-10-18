"""Caesar Cipher implementation."""

from cryptolab.exceptions import InvalidInputError


def _validate_caesar_params(text: str, shift: int) -> int:
    """Validate text and shift parameters for Caesar Cipher."""
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    if len(text) == 0:
        raise InvalidInputError("Input teks tidak boleh kosong.")
    if not isinstance(shift, int) or isinstance(shift, bool):
        raise InvalidInputError("Nilai pergeseran (shift) harus berupa bilangan bulat.")
    return shift % 26


def caesar_encrypt(text: str, shift: int) -> str:
    """Encrypt plaintext using Caesar Cipher.

    Args:
        text: Plaintext to be encrypted.
        shift: Number of positions to shift (can be 0, negative, or > 26).

    Returns:
        Encrypted ciphertext with spaces, punctuation, and casing preserved.

    Raises:
        InvalidInputError: If text is empty/invalid or shift is not an integer.
    """
    normalized_shift = _validate_caesar_params(text, shift)
    result = []
    for char in text:
        if "A" <= char <= "Z":
            shifted = chr(ord("A") + (ord(char) - ord("A") + normalized_shift) % 26)
            result.append(shifted)
        elif "a" <= char <= "z":
            shifted = chr(ord("a") + (ord(char) - ord("a") + normalized_shift) % 26)
            result.append(shifted)
        else:
            result.append(char)
    return "".join(result)


def caesar_decrypt(text: str, shift: int) -> str:
    """Decrypt ciphertext using Caesar Cipher.

    Args:
        text: Ciphertext to be decrypted.
        shift: Number of positions the text was originally shifted.

    Returns:
        Decrypted plaintext with spaces, punctuation, and casing preserved.

    Raises:
        InvalidInputError: If text is empty/invalid or shift is not an integer.
    """
    normalized_shift = _validate_caesar_params(text, shift)
    return caesar_encrypt(text, -normalized_shift)

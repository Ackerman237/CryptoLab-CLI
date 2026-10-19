"""Vigenere Cipher implementation."""

from typing import List
from ..exceptions import InvalidInputError, InvalidKeyError


def _validate_vigenere_params(text: str, key: str) -> List[int]:
    """Validate text and key parameters for Vigenere Cipher.

    Returns:
        List of integer shifts derived from the key letters (A=0, ..., Z=25).
    """
    if text is None or not isinstance(text, str):
        raise InvalidInputError("Input teks harus berupa string.")
    if len(text) == 0:
        raise InvalidInputError("Input teks tidak boleh kosong.")

    if key is None or not isinstance(key, str):
        raise InvalidKeyError("Kunci harus berupa string.")
    if len(key) == 0:
        raise InvalidKeyError("Kunci tidak boleh kosong.")

    shifts: List[int] = []
    for char in key:
        if "A" <= char <= "Z":
            shifts.append(ord(char) - ord("A"))
        elif "a" <= char <= "z":
            shifts.append(ord(char) - ord("a"))
        else:
            raise InvalidKeyError(
                f"Kunci hanya boleh berisi huruf alfabet (A-Z/a-z). Ditemukan karakter tidak valid: '{char}'."
            )

    if not shifts:
        raise InvalidKeyError("Kunci harus memiliki setidaknya satu huruf alfabet.")

    return shifts


def vigenere_encrypt(text: str, key: str) -> str:
    """Encrypt plaintext using Vigenere Cipher.

    Args:
        text: Plaintext to be encrypted.
        key: Alphabetic keyword for encryption.

    Returns:
        Encrypted ciphertext with spaces, punctuation, and casing preserved.

    Raises:
        InvalidInputError: If text is empty or invalid.
        InvalidKeyError: If key is empty or contains non-alphabetic characters.
    """
    shifts = _validate_vigenere_params(text, key)
    key_len = len(shifts)
    key_idx = 0
    result: List[str] = []

    for char in text:
        if "A" <= char <= "Z":
            shift = shifts[key_idx % key_len]
            shifted = chr(ord("A") + (ord(char) - ord("A") + shift) % 26)
            result.append(shifted)
            key_idx += 1
        elif "a" <= char <= "z":
            shift = shifts[key_idx % key_len]
            shifted = chr(ord("a") + (ord(char) - ord("a") + shift) % 26)
            result.append(shifted)
            key_idx += 1
        else:
            # Preserve spaces, digits, and punctuation without advancing key
            result.append(char)

    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """Decrypt ciphertext using Vigenere Cipher.

    Args:
        text: Ciphertext to be decrypted.
        key: Alphabetic keyword used during encryption.

    Returns:
        Decrypted plaintext with spaces, punctuation, and casing preserved.

    Raises:
        InvalidInputError: If text is empty or invalid.
        InvalidKeyError: If key is empty or contains non-alphabetic characters.
    """
    shifts = _validate_vigenere_params(text, key)
    key_len = len(shifts)
    key_idx = 0
    result: List[str] = []

    for char in text:
        if "A" <= char <= "Z":
            shift = shifts[key_idx % key_len]
            shifted = chr(ord("A") + (ord(char) - ord("A") - shift) % 26)
            result.append(shifted)
            key_idx += 1
        elif "a" <= char <= "z":
            shift = shifts[key_idx % key_len]
            shifted = chr(ord("a") + (ord(char) - ord("a") - shift) % 26)
            result.append(shifted)
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)

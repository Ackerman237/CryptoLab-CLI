"""Affine Cipher Implementation.

Monoalphabetic substitution cipher using affine transformation:
E(x) = (a * x + b) mod 26
D(y) = a^-1 * (y - b) mod 26

Where a must be coprime with 26 (a in {1,3,5,7,9,11,15,17,19,21,23,25}).
"""

import math
from dataclasses import dataclass
from typing import List, Optional

from cryptolab.exceptions import CryptoLabError, InvalidInputError, InvalidKeyError


# Valid 'a' values (coprime with 26)
VALID_A_VALUES = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]


@dataclass
class AffineResult:
    """Result of an Affine cipher operation."""
    a: int
    b: int
    a_inv: Optional[int]
    input_text: str
    output_text: str
    operation: str  # "encrypt" or "decrypt"
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = None


def _mod_inverse(a: int, m: int = 26) -> Optional[int]:
    """Find modular inverse of a modulo m."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def _validate_key(a: int, b: int) -> None:
    """Validate affine cipher key parameters."""
    if a not in VALID_A_VALUES:
        raise InvalidKeyError(
            f"'a' harus relatif prima dengan 26. "
            f"Nilai valid: {VALID_A_VALUES}. Ditemukan: {a}"
        )
    if not (0 <= b < 26):
        raise InvalidKeyError(f"'b' harus 0-25. Ditemukan: {b}")


def _process_char(char: str, a: int, b: int, encrypt: bool) -> str:
    """Process single character with affine transformation."""
    if not char.isalpha():
        return char
    
    is_upper = char.isupper()
    x = ord(char.upper()) - ord('A')
    
    if encrypt:
        y = (a * x + b) % 26
    else:
        a_inv = _mod_inverse(a, 26)
        if a_inv is None:
            raise InvalidKeyError(f"Tidak ada invers modular untuk a={a} modulo 26.")
        y = (a_inv * (x - b)) % 26
    
    result = chr(y + ord('A'))
    return result if is_upper else result.lower()


def affine_encrypt(plaintext: str, a: int, b: int) -> AffineResult:
    """Encrypt plaintext using Affine cipher.
    
    Args:
        plaintext: Text to encrypt (preserves case, non-letters unchanged).
        a: Multiplicative key (must be coprime with 26).
        b: Additive key (0-25).
        
    Returns:
        AffineResult with ciphertext.
    """
    _validate_key(a, b)
    
    if not plaintext:
        raise InvalidInputError("Plaintext tidak boleh kosong.")
    
    a_inv = _mod_inverse(a, 26)
    ciphertext = "".join(_process_char(c, a, b, encrypt=True) for c in plaintext)
    
    return AffineResult(
        a=a,
        b=b,
        a_inv=a_inv,
        input_text=plaintext,
        output_text=ciphertext,
        operation="encrypt",
        technical_success=True,
        status_message=f"Enkripsi Affine Cipher (a={a}, b={b}) berhasil.",
        reasons=[f"E(x) = ({a}x + {b}) mod 26", f"Invers a: {a_inv}", f"Valid a values: {VALID_A_VALUES}"],
    )


def affine_decrypt(ciphertext: str, a: int, b: int) -> AffineResult:
    """Decrypt ciphertext using Affine cipher.
    
    Args:
        ciphertext: Text to decrypt (preserves case, non-letters unchanged).
        a: Multiplicative key (must be coprime with 26).
        b: Additive key (0-25).
        
    Returns:
        AffineResult with plaintext.
    """
    _validate_key(a, b)
    
    if not ciphertext:
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    
    a_inv = _mod_inverse(a, 26)
    if a_inv is None:
        raise InvalidKeyError(f"Tidak ada invers modular untuk a={a} modulo 26.")
    
    plaintext = "".join(_process_char(c, a, b, encrypt=False) for c in ciphertext)
    
    return AffineResult(
        a=a,
        b=b,
        a_inv=a_inv,
        input_text=ciphertext,
        output_text=plaintext,
        operation="decrypt",
        technical_success=True,
        status_message=f"Dekripsi Affine Cipher (a={a}, b={b}) berhasil.",
        reasons=[f"D(y) = {a_inv}(y - {b}) mod 26", f"Invers a: {a_inv}"],
    )


def affine_brute_force(ciphertext: str) -> List[AffineResult]:
    """Try all valid affine keys to decrypt ciphertext.
    
    Returns:
        List of AffineResult candidates for all valid (a,b) pairs.
    """
    if not ciphertext:
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    
    candidates = []
    for a in VALID_A_VALUES:
        a_inv = _mod_inverse(a, 26)
        if a_inv is None:
            continue
        for b in range(26):
            try:
                res = affine_decrypt(ciphertext, a, b)
                candidates.append(res)
            except Exception:
                continue
    
    return candidates


__all__ = [
    "affine_encrypt",
    "affine_decrypt",
    "affine_brute_force",
    "AffineResult",
    "VALID_A_VALUES",
]
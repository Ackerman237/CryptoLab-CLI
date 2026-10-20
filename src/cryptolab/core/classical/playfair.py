"""Playfair Cipher Implementation.

Digram substitution cipher using a 5x5 key matrix.
Traditional 25-letter alphabet (I/J combined).
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

from ..exceptions import CryptoLabError, InvalidInputError, InvalidKeyError


@dataclass
class PlayfairResult:
    """Result of a Playfair cipher operation."""
    key_matrix: List[List[str]]
    input_text: str
    output_text: str
    operation: str  # "encrypt" or "decrypt"
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = None


def _build_playfair_matrix(key: str) -> List[List[str]]:
    """Build 5x5 Playfair matrix from key.
    
    Args:
        key: Keyword for matrix generation (letters only, no spaces).
        
    Returns:
        5x5 matrix as list of lists.
    """
    # Normalize key: uppercase, remove non-alpha, replace J with I
    key = "".join(c.upper() for c in key if c.isalpha()).replace("J", "I")
    
    # Build unique letter sequence from key + remaining alphabet
    seen = set()
    matrix_letters = []
    
    for c in key:
        if c not in seen:
            seen.add(c)
            matrix_letters.append(c)
    
    # Add remaining alphabet (A-Z except J)
    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in seen:
            seen.add(c)
            matrix_letters.append(c)
    
    # Form 5x5 matrix
    matrix = []
    for i in range(0, 25, 5):
        matrix.append(matrix_letters[i:i+5])
    
    return matrix


def _find_position(matrix: List[List[str]], char: str) -> Tuple[int, int]:
    """Find row, col of character in matrix."""
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val == char:
                return (r, c)
    raise ValueError(f"Character {char} not found in matrix")


def _prepare_text(text: str, for_encryption: bool = True) -> str:
    """Prepare text for Playfair processing.
    
    For encryption: remove non-alpha, replace J with I, split into digrams,
    insert X between double letters, pad with X if odd length.
    For decryption: just normalize (uppercase, remove non-alpha, J->I).
    """
    # Normalize
    normalized = "".join(c.upper() for c in text if c.isalpha()).replace("J", "I")
    
    if not for_encryption:
        return normalized
    
    # Split into digrams with X insertion
    digrams = []
    i = 0
    while i < len(normalized):
        if i + 1 >= len(normalized):
            # Last single letter - pad with X
            digrams.append(normalized[i] + "X")
            break
        
        if normalized[i] == normalized[i + 1]:
            # Double letter - insert X
            digrams.append(normalized[i] + "X")
            i += 1
        else:
            digrams.append(normalized[i:i+2])
            i += 2
    
    return "".join(digrams)


def _playfair_process(digrams: str, matrix: List[List[str]], encrypt: bool) -> str:
    """Process digrams through Playfair cipher."""
    if len(digrams) % 2 != 0:
        raise InvalidInputError("Processed text must have even length (digrams).")
    
    result = []
    direction = 1 if encrypt else -1
    
    for i in range(0, len(digrams), 2):
        a, b = digrams[i], digrams[i+1]
        r1, c1 = _find_position(matrix, a)
        r2, c2 = _find_position(matrix, b)
        
        if r1 == r2:
            # Same row - shift columns
            c1_new = (c1 + direction) % 5
            c2_new = (c2 + direction) % 5
            result.append(matrix[r1][c1_new])
            result.append(matrix[r2][c2_new])
        elif c1 == c2:
            # Same column - shift rows
            r1_new = (r1 + direction) % 5
            r2_new = (r2 + direction) % 5
            result.append(matrix[r1_new][c1])
            result.append(matrix[r2_new][c2])
        else:
            # Rectangle - swap columns
            result.append(matrix[r1][c2])
            result.append(matrix[r2][c1])
    
    return "".join(result)


def playfair_encrypt(plaintext: str, key: str) -> PlayfairResult:
    """Encrypt plaintext using Playfair cipher.
    
    Args:
        plaintext: Text to encrypt.
        key: Keyword for matrix generation.
        
    Returns:
        PlayfairResult with ciphertext (no spaces, uppercase).
    """
    if not plaintext or not plaintext.strip():
        raise InvalidInputError("Plaintext tidak boleh kosong.")
    if not key or not key.strip():
        raise InvalidKeyError("Key tidak boleh kosong.")
    
    matrix = _build_playfair_matrix(key)
    prepared = _prepare_text(plaintext, for_encryption=True)
    ciphertext = _playfair_process(prepared, matrix, encrypt=True)
    
    return PlayfairResult(
        key_matrix=matrix,
        input_text=plaintext,
        output_text=ciphertext,
        operation="encrypt",
        technical_success=True,
        status_message="Enkripsi Playfair berhasil.",
        reasons=[f"Key matrix: 5x5 dari '{key.upper().replace('J','I')}'", "Digrams diproses dengan aturan Playfair"],
    )


def playfair_decrypt(ciphertext: str, key: str) -> PlayfairResult:
    """Decrypt ciphertext using Playfair cipher.
    
    Args:
        ciphertext: Text to decrypt (uppercase, no spaces).
        key: Keyword for matrix generation.
        
    Returns:
        PlayfairResult with plaintext (may contain padding X).
    """
    if not ciphertext or not ciphertext.strip():
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    if not key or not key.strip():
        raise InvalidKeyError("Key tidak boleh kosong.")
    
    matrix = _build_playfair_matrix(key)
    normalized = _prepare_text(ciphertext, for_encryption=False)
    plaintext = _playfair_process(normalized, matrix, encrypt=False)
    
    return PlayfairResult(
        key_matrix=matrix,
        input_text=ciphertext,
        output_text=plaintext,
        operation="decrypt",
        technical_success=True,
        status_message="Dekripsi Playfair berhasil. Hasil mungkin mengandung padding 'X'.",
        reasons=[f"Key matrix: 5x5 dari '{key.upper().replace('J','I')}'", "Digrams diproses dengan aturan Playfair terbalik"],
    )


def format_matrix(matrix: List[List[str]]) -> str:
    """Format matrix for display."""
    return "\n".join("  " + " ".join(row) for row in matrix)


__all__ = [
    "playfair_encrypt",
    "playfair_decrypt",
    "format_matrix",
    "PlayfairResult",
]
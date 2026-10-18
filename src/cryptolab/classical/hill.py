"""Hill Cipher Implementation.

Polygraphic substitution cipher using matrix multiplication modulo 26.
Supports 2x2 and 3x3 matrix sizes.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from cryptolab.exceptions import CryptoLabError, InvalidInputError, InvalidKeyError


@dataclass
class HillResult:
    """Result of a Hill cipher operation."""
    key_matrix: List[List[int]]
    matrix_size: int
    input_text: str
    output_text: str
    operation: str  # "encrypt" or "decrypt"
    determinant: int
    determinant_inv: Optional[int]
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = None


def _mod_inverse(a: int, m: int = 26) -> Optional[int]:
    """Find modular inverse of a modulo m using Extended Euclidean Algorithm."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def _matrix_determinant(matrix: List[List[int]]) -> int:
    """Calculate determinant of 2x2 or 3x3 matrix modulo 26."""
    n = len(matrix)
    if n == 2:
        return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
    elif n == 3:
        # Sarrus rule for 3x3
        det = (
            matrix[0][0] * matrix[1][1] * matrix[2][2]
            + matrix[0][1] * matrix[1][2] * matrix[2][0]
            + matrix[0][2] * matrix[1][0] * matrix[2][1]
            - matrix[0][2] * matrix[1][1] * matrix[2][0]
            - matrix[0][1] * matrix[1][0] * matrix[2][2]
            - matrix[0][0] * matrix[1][2] * matrix[2][1]
        )
        return det % 26
    raise InvalidInputError("Hanya mendukung matrix 2x2 atau 3x3.")


def _matrix_inverse(matrix: List[List[int]]) -> List[List[int]]:
    """Calculate inverse matrix modulo 26."""
    n = len(matrix)
    det = _matrix_determinant(matrix)
    det_inv = _mod_inverse(det, 26)
    
    if det_inv is None:
        raise InvalidKeyError(
            f"Matrix tidak invertible modulo 26. Determinan = {det}, "
            f"tidak memiliki invers modulo 26 (gcd({det}, 26) != 1)."
        )
    
    if n == 2:
        # Adjugate for 2x2: [[d, -b], [-c, a]]
        inv = [
            [matrix[1][1] % 26, (-matrix[0][1]) % 26],
            [(-matrix[1][0]) % 26, matrix[0][0] % 26],
        ]
    elif n == 3:
        # Adjugate for 3x3 (transpose of cofactor matrix)
        m = matrix
        inv = [
            [
                (m[1][1] * m[2][2] - m[1][2] * m[2][1]) % 26,
                (m[0][2] * m[2][1] - m[0][1] * m[2][2]) % 26,
                (m[0][1] * m[1][2] - m[0][2] * m[1][1]) % 26,
            ],
            [
                (m[1][2] * m[2][0] - m[1][0] * m[2][2]) % 26,
                (m[0][0] * m[2][2] - m[0][2] * m[2][0]) % 26,
                (m[0][2] * m[1][0] - m[0][0] * m[1][2]) % 26,
            ],
            [
                (m[1][0] * m[2][1] - m[1][1] * m[2][0]) % 26,
                (m[0][1] * m[2][0] - m[0][0] * m[2][1]) % 26,
                (m[0][0] * m[1][1] - m[0][1] * m[1][0]) % 26,
            ],
        ]
    else:
        raise InvalidInputError("Hanya mendukung matrix 2x2 atau 3x3.")
    
    # Multiply by determinant inverse
    return [[(det_inv * val) % 26 for val in row] for row in inv]


def _matrix_multiply(matrix: List[List[int]], vector: List[int]) -> List[int]:
    """Multiply matrix (n x n) with vector (n x 1) modulo 26."""
    n = len(matrix)
    result = []
    for i in range(n):
        total = sum(matrix[i][j] * vector[j] for j in range(n))
        result.append(total % 26)
    return result


def _parse_key_matrix(key_str: str, size: int) -> List[List[int]]:
    """Parse key string into n x n matrix.
    
    Key format: "a b c d e f g h i" for 3x3 or "a b c d" for 2x2
    Numbers are space-separated integers 0-25.
    """
    parts = key_str.strip().split()
    expected = size * size
    
    if len(parts) != expected:
        raise InvalidInputError(
            f"Key matrix {size}x{size} butuh {expected} angka (0-25). "
            f"Ditemukan: {len(parts)}."
        )
    
    try:
        numbers = [int(x) % 26 for x in parts]
    except ValueError:
        raise InvalidInputError("Key harus berisi angka integer 0-25.")
    
    matrix = []
    for i in range(0, expected, size):
        matrix.append(numbers[i:i+size])
    
    return matrix


def _prepare_text(text: str, size: int) -> List[List[int]]:
    """Convert text to list of numeric vectors (A=0, B=1, ... Z=25).
    Pad with 'X' (23) if needed.
    """
    # Normalize: keep only letters, uppercase, replace J with I
    normalized = "".join(c.upper() for c in text if c.isalpha()).replace("J", "I")
    
    if not normalized:
        raise InvalidInputError("Teks tidak mengandung huruf valid.")
    
    # Convert to numbers
    numbers = [ord(c) - ord('A') for c in normalized]
    
    # Pad with X (23) to make length multiple of size
    while len(numbers) % size != 0:
        numbers.append(23)  # X
    
    # Group into vectors
    vectors = []
    for i in range(0, len(numbers), size):
        vectors.append(numbers[i:i+size])
    
    return vectors


def _vectors_to_text(vectors: List[List[int]]) -> str:
    """Convert list of numeric vectors back to text."""
    chars = []
    for vec in vectors:
        for val in vec:
            chars.append(chr(val + ord('A')))
    return "".join(chars)


def hill_encrypt(plaintext: str, key_str: str, size: int = 2) -> HillResult:
    """Encrypt plaintext using Hill cipher.
    
    Args:
        plaintext: Text to encrypt.
        key_str: Space-separated key matrix numbers (0-25).
        size: Matrix size (2 for 2x2, 3 for 3x3).
        
    Returns:
        HillResult with ciphertext.
    """
    if size not in (2, 3):
        raise InvalidInputError("Ukuran matrix harus 2 atau 3.")
    if not plaintext or not plaintext.strip():
        raise InvalidInputError("Plaintext tidak boleh kosong.")
    if not key_str or not key_str.strip():
        raise InvalidKeyError("Key matrix tidak boleh kosong.")
    
    key_matrix = _parse_key_matrix(key_str, size)
    det = _matrix_determinant(key_matrix)
    det_inv = _mod_inverse(det, 26)
    
    # Verify key is invertible
    if det_inv is None:
        raise InvalidKeyError(
            f"Matrix tidak invertible modulo 26. Determinan = {det}. "
            f"gcd({det}, 26) = {math.gcd(det, 26)} != 1."
        )
    
    vectors = _prepare_text(plaintext, size)
    cipher_vectors = [_matrix_multiply(key_matrix, vec) for vec in vectors]
    ciphertext = _vectors_to_text(cipher_vectors)
    
    return HillResult(
        key_matrix=key_matrix,
        matrix_size=size,
        input_text=plaintext,
        output_text=ciphertext,
        operation="encrypt",
        determinant=det,
        determinant_inv=det_inv,
        technical_success=True,
        status_message=f"Enkripsi Hill Cipher {size}x{size} berhasil.",
        reasons=[f"Determinan: {det}", f"Invers determinan: {det_inv}", f"Matrix invertible modulo 26"],
    )


def hill_decrypt(ciphertext: str, key_str: str, size: int = 2) -> HillResult:
    """Decrypt ciphertext using Hill cipher.
    
    Args:
        ciphertext: Text to decrypt.
        key_str: Space-separated key matrix numbers (0-25).
        size: Matrix size (2 for 2x2, 3 for 3x3).
        
    Returns:
        HillResult with plaintext (may contain padding X).
    """
    if size not in (2, 3):
        raise InvalidInputError("Ukuran matrix harus 2 atau 3.")
    if not ciphertext or not ciphertext.strip():
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    if not key_str or not key_str.strip():
        raise InvalidKeyError("Key matrix tidak boleh kosong.")
    
    key_matrix = _parse_key_matrix(key_str, size)
    det = _matrix_determinant(key_matrix)
    det_inv = _mod_inverse(det, 26)
    
    if det_inv is None:
        raise InvalidKeyError(
            f"Matrix tidak invertible modulo 26. Determinan = {det}."
        )
    
    inv_matrix = _matrix_inverse(key_matrix)
    vectors = _prepare_text(ciphertext, size)
    plain_vectors = [_matrix_multiply(inv_matrix, vec) for vec in vectors]
    plaintext = _vectors_to_text(plain_vectors)
    
    return HillResult(
        key_matrix=key_matrix,
        matrix_size=size,
        input_text=ciphertext,
        output_text=plaintext,
        operation="decrypt",
        determinant=det,
        determinant_inv=det_inv,
        technical_success=True,
        status_message=f"Dekripsi Hill Cipher {size}x{size} berhasil. Hasil mungkin mengandung padding 'X'.",
        reasons=[f"Determinan: {det}", f"Invers determinan: {det_inv}", f"Invers matrix dihitung modulo 26"],
    )


def format_matrix(matrix: List[List[int]]) -> str:
    """Format matrix for display."""
    return "\n".join("  " + " ".join(f"{val:2d}" for val in row) for row in matrix)


__all__ = [
    "hill_encrypt",
    "hill_decrypt",
    "format_matrix",
    "HillResult",
]
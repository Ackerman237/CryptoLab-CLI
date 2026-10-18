"""Rail Fence / Transposition Cipher Implementation.

Transposition cipher that writes plaintext in a zig-zag pattern
across multiple "rails" and reads off row by row.
"""

from dataclasses import dataclass
from typing import List, Optional

from cryptolab.exceptions import CryptoLabError, InvalidInputError


@dataclass
class RailFenceResult:
    """Result of a Rail Fence cipher operation."""
    rails: int
    input_text: str
    output_text: str
    operation: str  # "encrypt" or "decrypt"
    technical_success: bool = True
    status_message: str = ""
    reasons: List[str] = None
    rail_pattern: List[List[str]] = None


def _build_fence_pattern(text_len: int, rails: int) -> List[List[Optional[int]]]:
    """Build rail fence pattern as list of lists with position indices."""
    if rails < 2:
        raise InvalidInputError("Jumlah rail minimal 2.")
    if rails > text_len:
        raise InvalidInputError("Jumlah rail tidak boleh melebihi panjang teks.")
    
    # Create empty fence
    fence = [[None for _ in range(text_len)] for _ in range(rails)]
    
    rail = 0
    direction = 1  # 1 = down, -1 = up
    
    for pos in range(text_len):
        fence[rail][pos] = pos
        rail += direction
        
        if rail == rails - 1 or rail == 0:
            direction *= -1
    
    return fence


def _rail_fence_encrypt(plaintext: str, rails: int) -> str:
    """Encrypt using rail fence cipher."""
    if not plaintext:
        return ""
    
    fence = _build_fence_pattern(len(plaintext), rails)
    
    # Read off by rails
    ciphertext = []
    for r in range(rails):
        for c in range(len(plaintext)):
            if fence[r][c] is not None:
                ciphertext.append(plaintext[fence[r][c]])
    
    return "".join(ciphertext)


def _rail_fence_decrypt(ciphertext: str, rails: int) -> str:
    """Decrypt using rail fence cipher."""
    if not ciphertext:
        return ""
    
    fence = _build_fence_pattern(len(ciphertext), rails)
    
    # Fill fence with ciphertext letters in rail order
    idx = 0
    for r in range(rails):
        for c in range(len(ciphertext)):
            if fence[r][c] is not None:
                fence[r][c] = ciphertext[idx]
                idx += 1
    
    # Read off in zig-zag order
    plaintext = []
    rail = 0
    direction = 1
    for pos in range(len(ciphertext)):
        plaintext.append(fence[rail][pos])
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction *= -1
    
    return "".join(plaintext)


def _build_rail_display(text: str, rails: int) -> List[List[str]]:
    """Build visual rail pattern for display."""
    fence = _build_fence_pattern(len(text), rails)
    display = []
    for r in range(rails):
        row = []
        for c in range(len(text)):
            if fence[r][c] is not None:
                row.append(text[fence[r][c]])
            else:
                row.append(".")
        display.append(row)
    return display


def railfence_encrypt(plaintext: str, rails: int) -> RailFenceResult:
    """Encrypt plaintext using Rail Fence cipher.
    
    Args:
        plaintext: Text to encrypt.
        rails: Number of rails (2+).
        
    Returns:
        RailFenceResult with ciphertext and rail pattern.
    """
    if not plaintext or not plaintext.strip():
        raise InvalidInputError("Plaintext tidak boleh kosong.")
    
    ciphertext = _rail_fence_encrypt(plaintext, rails)
    rail_pattern = _build_rail_display(plaintext, rails)
    
    return RailFenceResult(
        rails=rails,
        input_text=plaintext,
        output_text=ciphertext,
        operation="encrypt",
        technical_success=True,
        status_message=f"Enkripsi Rail Fence {rails} rail berhasil.",
        reasons=[f"Pola zig-zag pada {rails} rail", f"Panjang teks: {len(plaintext)}"],
        rail_pattern=rail_pattern,
    )


def railfence_decrypt(ciphertext: str, rails: int) -> RailFenceResult:
    """Decrypt ciphertext using Rail Fence cipher.
    
    Args:
        ciphertext: Text to decrypt.
        rails: Number of rails (2+).
        
    Returns:
        RailFenceResult with plaintext and rail pattern.
    """
    if not ciphertext or not ciphertext.strip():
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    
    plaintext = _rail_fence_decrypt(ciphertext, rails)
    rail_pattern = _build_rail_display(plaintext, rails)
    
    return RailFenceResult(
        rails=rails,
        input_text=ciphertext,
        output_text=plaintext,
        operation="decrypt",
        technical_success=True,
        status_message=f"Dekripsi Rail Fence {rails} rail berhasil.",
        reasons=[f"Pola zig-zag pada {rails} rail", f"Panjang teks: {len(ciphertext)}"],
        rail_pattern=rail_pattern,
    )


def railfence_brute_force(ciphertext: str, max_rails: int = 10) -> List[RailFenceResult]:
    """Try decrypting with different rail counts.
    
    Args:
        ciphertext: Text to decrypt.
        max_rails: Maximum number of rails to try.
        
    Returns:
        List of RailFenceResult candidates.
    """
    if not ciphertext:
        raise InvalidInputError("Ciphertext tidak boleh kosong.")
    
    candidates = []
    for rails in range(2, min(max_rails + 1, len(ciphertext) + 1)):
        try:
            res = railfence_decrypt(ciphertext, rails)
            candidates.append(res)
        except Exception:
            continue
    
    return candidates


def format_rail_pattern(pattern: List[List[str]]) -> str:
    """Format rail pattern for display."""
    lines = []
    for i, row in enumerate(pattern):
        lines.append(f"  Rail {i}: {' '.join(row)}")
    return "\n".join(lines)


__all__ = [
    "railfence_encrypt",
    "railfence_decrypt",
    "railfence_brute_force",
    "format_rail_pattern",
    "RailFenceResult",
]
"""Classical ciphers module (Caesar, Vigenere, Playfair, Hill, Affine, Rail Fence). Backward compatibility."""

from cryptolab.core.classical import (
    caesar_encrypt,
    caesar_decrypt,
    vigenere_encrypt,
    vigenere_decrypt,
    playfair_encrypt,
    playfair_decrypt,
    format_matrix,
    PlayfairResult,
    hill_encrypt,
    hill_decrypt,
    format_matrix as hill_format_matrix,
    HillResult,
    affine_encrypt,
    affine_decrypt,
    affine_brute_force,
    AffineResult,
    VALID_A_VALUES,
    railfence_encrypt,
    railfence_decrypt,
    railfence_brute_force,
    format_rail_pattern,
    RailFenceResult,
)

__all__ = [
    "caesar_encrypt", "caesar_decrypt",
    "vigenere_encrypt", "vigenere_decrypt",
    "playfair_encrypt", "playfair_decrypt", "format_matrix", "PlayfairResult",
    "hill_encrypt", "hill_decrypt", "hill_format_matrix", "HillResult",
    "affine_encrypt", "affine_decrypt", "affine_brute_force", "AffineResult", "VALID_A_VALUES",
    "railfence_encrypt", "railfence_decrypt", "railfence_brute_force", "format_rail_pattern", "RailFenceResult",
]
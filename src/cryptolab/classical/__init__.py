"""Classical ciphers module (Caesar, Vigenere, Playfair, Hill, Affine, Rail Fence)."""

from cryptolab.classical.caesar import caesar_encrypt, caesar_decrypt
from cryptolab.classical.vigenere import vigenere_encrypt, vigenere_decrypt
from cryptolab.classical.playfair import playfair_encrypt, playfair_decrypt, format_matrix, PlayfairResult
from cryptolab.classical.hill import hill_encrypt, hill_decrypt, format_matrix as hill_format_matrix, HillResult
from cryptolab.classical.affine import affine_encrypt, affine_decrypt, affine_brute_force, AffineResult, VALID_A_VALUES
from cryptolab.classical.railfence import railfence_encrypt, railfence_decrypt, railfence_brute_force, format_rail_pattern, RailFenceResult

__all__ = [
    "caesar_encrypt", "caesar_decrypt",
    "vigenere_encrypt", "vigenere_decrypt",
    "playfair_encrypt", "playfair_decrypt", "format_matrix", "PlayfairResult",
    "hill_encrypt", "hill_decrypt", "hill_format_matrix", "HillResult",
    "affine_encrypt", "affine_decrypt", "affine_brute_force", "AffineResult", "VALID_A_VALUES",
    "railfence_encrypt", "railfence_decrypt", "railfence_brute_force", "format_rail_pattern", "RailFenceResult",
]

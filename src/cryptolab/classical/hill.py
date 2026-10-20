"""Hill Cipher implementation. Backward compatibility."""

from cryptolab.core.classical.hill import hill_encrypt, hill_decrypt, format_matrix as hill_format_matrix, HillResult

__all__ = ["hill_encrypt", "hill_decrypt", "hill_format_matrix", "HillResult"]